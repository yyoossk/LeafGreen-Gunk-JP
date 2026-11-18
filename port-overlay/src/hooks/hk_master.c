#include "global.h"
#include "event_data.h"
#include "pokemon.h"
#include "random.h"
#include "string_util.h"
#include "battle.h"
#include "task.h"
#include "list_menu.h"
#include "window.h"
#include "malloc.h"
#include "sound.h"
#include "script.h"
#include "menu_indicators.h"
#include "event_object_movement.h"
#include "load_save.h"
#include "script_pokemon_util.h"
#include "constants/species.h"
#include "constants/items.h"
#include "constants/moves.h"
#include "constants/songs.h"
#include "constants/flags.h"
#include "constants/event_objects.h"
#include "constants/event_object_movement.h"
// FRLG+ Master Trainers (JP port).
// 151 Master Trainers appear around Kanto once the player is Champion (object flag FLAG_JP_HIDE_MASTERS, kept in
// sync with FLAG_SYS_GAME_CLEAR on every warp). Each one battles a single Pokémon of their species, one-on-one,
// at the level of the player's lead (which must be the same species); no items. A win gives a title.
// Ditto, Articuno, Zapdos, Moltres, Mewtwo and Mew only want to see one with 100 total EVs.
// All 151 titles open a battle with Professor Oak (GRAND MASTER).
//
// Trainer ids: JP_MASTER_BASE + species - 1 (750-900), Oak = 901, appended to the relocated gTrainers.
// Progress lives in vars: VAR_JP_MASTER_FLAGS..+9 (bit n = species n, bit 0 = Oak), VAR_JP_MASTER_TITLE.

#define JP_MASTER_BASE 750
#define JP_MASTER_OAK (JP_MASTER_BASE + 151)
#define VAR_JP_MASTER_FLAGS 0x408E
#define VAR_JP_MASTER_TITLE 0x4098
#define FLAG_JP_HIDE_MASTERS 0x0EA
#define TITLE_GRAND 152
#define TITLE_CANCEL 153

struct JpMasterMon
{
    u8 iv, nature, abilityNum, lvl;
    u8 evs[NUM_STATS];
    u16 species, heldItem;
    u16 moves[MAX_MON_MOVES];
};
#include "gen/master_data.h"

extern const u8 *const gJpMasterScripts[152];
extern const u8 *const gJpMasterTexts[5 * 10];
extern void (*const sMovementTypeCallbacks[])(struct Sprite *);
extern u16 gTrainerBattleOpponent_A;

bool8 JpFlagGet(u16 id);
u8 JpCreateWindowFromRect(u8 x, u8 y, u8 w, u8 h);
void JpSetStdWindowBorderStyle(u8 windowId, bool8 copyToVram);
void JpScheduleBgCopyTilemapToVram(u8 bg);
void ClearStdWindowAndFrameToTransparent(u8 windowId, bool8 copyToVram);
#define JP_SCRIPT_CTX_DATA0 (*(u32 *)(0x03000EB0 + 0x64))   // sGlobalScriptContext.data[0]
#define JP_FONT_NORMAL 2

// ---------------------------------------------------------------- progress
static bool8 IsBeaten(u16 sp)
{
    return (VarGet(VAR_JP_MASTER_FLAGS + (sp >> 4)) >> (sp & 15)) & 1;
}

static void SetBeaten(u16 sp)
{
    VarSet(VAR_JP_MASTER_FLAGS + (sp >> 4), VarGet(VAR_JP_MASTER_FLAGS + (sp >> 4)) | (1 << (sp & 15)));
}

static bool8 HasAllTitles(void)
{
    u16 i;
    for (i = 1; i <= 151; i++)
        if (!IsBeaten(i))
            return FALSE;
    return TRUE;
}

// GetTrainerAFlag (JP 0x0807F73C): Master Trainers / Oak have no trainer flag (flag 0 is a no-op)
u16 JpGetTrainerAFlag(void)
{
    if (gTrainerBattleOpponent_A >= JP_MASTER_BASE)
        return 0;
    return 0x500 + gTrainerBattleOpponent_A;
}

static bool8 IsMasterBattle(void)
{
    return gTrainerBattleOpponent_A >= JP_MASTER_BASE && gTrainerBattleOpponent_A < JP_MASTER_OAK;
}

// CB2_EndTrainerBattle's IsPlayerDefeated: losing to a Master Trainer doesn't white out (the script restores the party)
bool8 IsPlayerDefeated(u32 battleOutcome);
bool8 JpMaster_EndDefeated(u32 battleOutcome)
{
    if (IsMasterBattle())
        return FALSE;
    return IsPlayerDefeated(battleOutcome);
}

extern u8 gBattleOutcome;
void JpMaster_GetLost(void)
{
    gSpecialVar_Result = (gBattleOutcome != B_OUTCOME_WON);
}

// HandleTurnActionSelectionState, B_ACTION_USE_ITEM: no items in a Master Trainer battle
u32 JpMaster_ItemBlock(u32 battleTypeFlags)
{
    u32 r = battleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_BATTLE_TOWER | BATTLE_TYPE_EREADER_TRAINER);
    if ((battleTypeFlags & BATTLE_TYPE_TRAINER) && IsMasterBattle())
        r |= BATTLE_TYPE_TRAINER;
    return r;
}

// keep the object flag in sync: the Master Trainers are out once the player is Champion (LoadMapFromWarp)
void JpMaster_SyncHideFlag(void)
{
    if (JpFlagGet(FLAG_SYS_GAME_CLEAR))
        FlagClear(FLAG_JP_HIDE_MASTERS);
    else
        FlagSet(FLAG_JP_HIDE_MASTERS);
}

// ---------------------------------------------------------------- parties
static const u8 sHiddenPowerIVs[12][NUM_STATS] = {
    [1]  = {31, 31, 30, 31, 31, 30},   // Ghost
    [2]  = {31, 31, 31, 31, 30, 30},   // Ground
    [3]  = {31, 31, 31, 30, 30, 30},   // Flying
    [4]  = {31, 31, 30, 30, 30, 30},   // Fighting
    [5]  = {31, 31, 31, 30, 31, 30},   // Bug
    [6]  = {31, 31, 30, 30, 31, 30},   // Rock
    [7]  = {31, 30, 31, 31, 30, 31},   // Grass
    [8]  = {31, 31, 31, 30, 31, 31},   // Ice
    [9]  = {31, 31, 30, 30, 30, 31},   // Fire
    [10] = {31, 31, 31, 31, 30, 31},   // Electric
    [11] = {31, 31, 31, 30, 30, 31},   // Water
};

// FRLG+ CreateMonWithGenderNatureAbility + the EV/move/item setup of F_TRAINER_PARTY_EVS
static void CreateMasterMon(struct Pokemon *mon, const struct JpMasterMon *m, u8 level, u8 gender)
{
    u32 personality;
    u8 ratio = gSpeciesInfo[m->species].genderRatio;
    u8 j, friendship = 255;

    do
    {
        personality = (Random() << 16) | Random();
    }
    while (personality % NUM_NATURES != m->nature
        || personality % 2 != m->abilityNum
        || (ratio != MON_GENDERLESS && ratio != MON_FEMALE && ratio != MON_MALE
            && GetGenderFromSpeciesAndPersonality(m->species, personality) != gender));

    if (m->iv >= 1 && m->iv <= 11)
    {
        CreateMon(mon, m->species, level, 0, TRUE, personality, OT_ID_RANDOM_NO_SHINY, 0);
        for (j = 0; j < NUM_STATS; j++)
            SetMonData(mon, MON_DATA_HP_IV + j, &sHiddenPowerIVs[m->iv][j]);
    }
    else
    {
        CreateMon(mon, m->species, level, (m->iv == 255) ? 31 : m->iv, TRUE, personality, OT_ID_RANDOM_NO_SHINY, 0);
    }
    SetMonData(mon, MON_DATA_HELD_ITEM, &m->heldItem);
    for (j = 0; j < MAX_MON_MOVES; j++)
    {
        SetMonData(mon, MON_DATA_MOVE1 + j, &m->moves[j]);
        SetMonData(mon, MON_DATA_PP1 + j, &gBattleMoves[m->moves[j]].pp);
    }
    for (j = 0; j < NUM_STATS; j++)
        SetMonData(mon, MON_DATA_HP_EV + j, &m->evs[j]);
    SetMonData(mon, MON_DATA_FRIENDSHIP, &friendship);
    CalculateMonStats(mon);
}

// called by JpCreateNPCTrainerPartyWrapper; returns the party size, or 0 if trainerNum isn't ours
u8 JpMaster_CreateParty(struct Pokemon *party, u16 trainerNum)
{
    u8 i;

    if (trainerNum == JP_MASTER_OAK)
    {
        ZeroEnemyPartyMons();
        for (i = 0; i < PARTY_SIZE; i++)
            CreateMasterMon(&party[i], &sOakMons[i], sOakMons[i].lvl, MON_MALE);
        return PARTY_SIZE;
    }
    if (trainerNum >= JP_MASTER_BASE && trainerNum < JP_MASTER_OAK)
    {
        u16 sp = trainerNum - JP_MASTER_BASE + 1;
        ZeroEnemyPartyMons();
        CreateMasterMon(&party[0], &sMasterMons[sp], GetMonData(&gPlayerParty[0], MON_DATA_LEVEL), sMasterGender[sp]);
        return 1;
    }
    return 0;
}

// ---------------------------------------------------------------- overworld
static u16 SpeciesForScript(const u8 *script)
{
    u16 i;
    if (script == NULL)
        return 0;
    for (i = 1; i <= 151; i++)
        if (gJpMasterScripts[i] == script)
            return i;
    return 0;
}

// TrySetupObjectEventSprite: a Master Trainer who hasn't given their title yet waves at the player
void JpMaster_AdjustSpawn(struct ObjectEvent *objectEvent, const struct ObjectEventTemplate *template, struct SpriteTemplate *spriteTemplate)
{
    u16 sp = SpeciesForScript(template->script);
    u8 type;

    if (sp == 0 || IsBeaten(sp))
        return;
    type = (objectEvent->graphicsId == OBJ_EVENT_GFX_SWIMMER_F_WATER) ? MOVEMENT_TYPE_RAISE_HAND_AND_SWIM : MOVEMENT_TYPE_RAISE_HAND_AND_STOP;
    objectEvent->movementType = type;
    objectEvent->facingDirection = DIR_SOUTH;
    objectEvent->movementDirection = DIR_SOUTH;
    spriteTemplate->callback = sMovementTypeCallbacks[type];
}

// ---------------------------------------------------------------- script natives
// VAR_0x8009 = species. Sets VAR_0x8006 = script class, VAR_0x8007 = has the title
void JpMaster_Prepare(void)
{
    u16 sp = gSpecialVar_0x8009;
    gSpecialVar_0x8006 = (sp < 152 && sMasterScriptClass[sp] != 0xFF) ? sMasterScriptClass[sp] : 4;
    gSpecialVar_0x8007 = (sp < 152) ? IsBeaten(sp) : FALSE;
}

// msgbox text: class VAR_0x8006, kind VAR_0x8005 (followed by callstd)
void JpMaster_LoadText(void)
{
    u16 c = gSpecialVar_0x8006, k = gSpecialVar_0x8005;
    if (c < 5 && k < 10)
        JP_SCRIPT_CTX_DATA0 = (u32)gJpMasterTexts[c * 10 + k];
}

void JpMaster_CheckSlot1(void)
{
    gSpecialVar_Result = (GetMonData(&gPlayerParty[0], MON_DATA_SPECIES_OR_EGG) == gSpecialVar_0x8009);
}

void JpMaster_CheckSlot1EVs(void)
{
    u16 total = 0;
    u8 i;
    for (i = 0; i < NUM_STATS; i++)
        total += GetMonData(&gPlayerParty[0], MON_DATA_HP_EV + i);
    gSpecialVar_Result = (total >= 100);
}

// the lead battles alone, healed; LoadPlayerParty puts the real party back afterwards
void JpMaster_SetupParty(void)
{
    u8 i;
    SavePlayerParty();
    for (i = 1; i < PARTY_SIZE; i++)
        ZeroMonData(&gPlayerParty[i]);
    CalculatePlayerPartyCount();
    HealPlayerParty();
}

void JpMaster_SetBeaten(void)
{
    SetBeaten(gSpecialVar_0x8009);
}

void JpMaster_CanBattleOak(void)
{
    gSpecialVar_Result = !IsBeaten(0) && HasAllTitles();
}

void JpMaster_HasAnyTitle(void)
{
    u16 i;
    gSpecialVar_Result = FALSE;
    for (i = 0; i <= 151; i++)
        if (IsBeaten(i))
            gSpecialVar_Result = TRUE;
}

// VAR_RESULT = current title; STR_VAR_2 = its species name (or GRAND)
static const u8 sText_Grand[] = _("グランド");
void JpMaster_BufferCurrentTitle(void)
{
    u16 t = VarGet(VAR_JP_MASTER_TITLE);
    gSpecialVar_Result = t;
    if (t == TITLE_GRAND)
        StringCopy(gStringVar2, sText_Grand);
    else if (t >= 1 && t <= 151)
        GetSpeciesName(gStringVar2, t);
}

void JpMaster_SetTitle(void)
{
    VarSet(VAR_JP_MASTER_TITLE, gSpecialVar_Result);
}

// ---------------------------------------------------------------- title list (FRLG+ LISTMENU_MASTER_TRAINER_TITLES)
struct TitleMenu
{
    struct ListMenuItem items[153];
    u8 names[153][12];
};
static EWRAM_DATA struct TitleMenu *sTitleMenu = NULL;
static EWRAM_DATA u16 sTitleScroll = 0;
static const u8 sText_NoTitle[] = _("しょうごう なし");
static const u8 sText_Master[] = _("マスター");
static const u8 sText_GrandMaster[] = _("グランドマスター");

static void Task_TitleMenu(u8 taskId)
{
    s16 *data = gTasks[taskId].data;
    s32 input = ListMenu_ProcessInput(data[0]);

    ListMenuGetScrollAndRow(data[0], &sTitleScroll, NULL);
    if (input == LIST_NOTHING_CHOSEN)
        return;
    PlaySE(SE_SELECT);
    if (data[2] != 0xFF)
        RemoveScrollIndicatorArrowPair(data[2]);
    gSpecialVar_Result = (input == LIST_CANCEL) ? TITLE_CANCEL : input;
    DestroyListMenuTask(data[0], NULL, NULL);
    ClearStdWindowAndFrameToTransparent(data[1], TRUE);
    RemoveWindow(data[1]);
    Free(sTitleMenu);
    sTitleMenu = NULL;
    DestroyTask(taskId);
    ScriptContext_Enable();
}

void JpMaster_TitleMenu(void)
{
    struct ListMenuTemplate t = {0};
    u16 n = 0, i;
    u8 windowId, taskId, rows;

    sTitleMenu = Alloc(sizeof(struct TitleMenu));
    sTitleMenu->items[n].label = sText_NoTitle;
    sTitleMenu->items[n++].index = 0;
    for (i = 1; i <= 151; i++)
    {
        if (!IsBeaten(i))
            continue;
        GetSpeciesName(sTitleMenu->names[n], i);
        StringAppend(sTitleMenu->names[n], sText_Master);
        sTitleMenu->items[n].label = sTitleMenu->names[n];
        sTitleMenu->items[n++].index = i;
    }
    if (IsBeaten(0))
    {
        sTitleMenu->items[n].label = sText_GrandMaster;
        sTitleMenu->items[n++].index = TITLE_GRAND;
    }
    rows = n < 6 ? n : 6;
    windowId = JpCreateWindowFromRect(16, 1, 13, rows * 2);
    JpSetStdWindowBorderStyle(windowId, FALSE);

    t.items = sTitleMenu->items;
    t.totalItems = n;
    t.maxShowed = rows;
    t.windowId = windowId;
    t.item_X = 8;
    t.cursor_X = 0;
    t.upText_Y = 0;
    t.cursorPal = 2;
    t.fillValue = 1;
    t.cursorShadowPal = 3;
    t.fontId = JP_FONT_NORMAL;
    t.scrollMultiple = LIST_MULTIPLE_SCROLL_DPAD;

    taskId = CreateTask(Task_TitleMenu, 80);
    gTasks[taskId].data[1] = windowId;
    gTasks[taskId].data[0] = ListMenuInit(&t, 0, 0);
    sTitleScroll = 0;
    gTasks[taskId].data[2] = 0xFF;
    if (n > rows)
        gTasks[taskId].data[2] = AddScrollIndicatorArrowPairParameterized(SCROLL_ARROW_UP, 16 * 8 + 13 * 4, 8, 8 + rows * 16, n - rows, 110, 110, &sTitleScroll);
    CopyWindowToVram(windowId, COPYWIN_FULL);
    JpScheduleBgCopyTilemapToVram(0);
}

// FRLG+ resetobjectmovementtype VAR_LAST_TALKED: back to the map's own movement type once the title is given
const struct ObjectEventTemplate *GetObjectEventTemplateByLocalIdAndMap(u8 localId, u8 mapNum, u8 mapGroup);
void SetTrainerMovementType(struct ObjectEvent *objectEvent, u8 movementType);
void JpMaster_ResetMovementType(void)
{
    u8 mapNum = gSaveBlock1Ptr->location.mapNum, mapGroup = gSaveBlock1Ptr->location.mapGroup;
    u8 id = GetObjectEventIdByLocalIdAndMap(gSpecialVar_LastTalked, mapNum, mapGroup);
    const struct ObjectEventTemplate *t = GetObjectEventTemplateByLocalIdAndMap(gSpecialVar_LastTalked, mapNum, mapGroup);

    if (id < OBJECT_EVENTS_COUNT && t != NULL)
        SetTrainerMovementType(&gObjectEvents[id], t->objUnion.normal.movementType);
}
