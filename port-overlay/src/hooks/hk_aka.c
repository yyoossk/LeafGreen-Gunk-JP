#include "global.h"
#include "event_data.h"
#include "field_player_avatar.h"
#include "overworld.h"
#include "pokemon.h"
#include "pokedex.h"
#include "string_util.h"
#include "sound.h"
#include "constants/songs.h"
#include "constants/region_map_sections.h"
#include "constants/flags.h"
#include "constants/species.h"
#include "script.h"
#include "task.h"
#include "menu.h"
#include "new_menu_helpers.h"
#include "text_window.h"
#include "window.h"
#include "text.h"
#include "fieldmap.h"
#include "quest_log.h"
#include "constants/quest_log.h"
#include "safari_zone.h"
#include "save.h"
#include "pokemon_storage_system.h"
#include "constants/game_stat.h"
// 赤フルカラーの機能を ファイアレッドに

bool8 TryRunOnFrameMapScript(void);
void SetCurrentBox(u8 boxId);
#define FLAG_JP_BIKE_GEAR 0x0E3
#define JP_BOXES 16

extern const u8 EventScript_JpBoxSwitched[];

static u8 CountMonsInJpBox(u8 box)
{
    u8 i, n = 0;
    for (i = 0; i < IN_BOX_COUNT; i++)
        if (GetBoxMonDataAt(box, i, MON_DATA_SPECIES) != SPECIES_NONE)
            n++;
    return n;
}

// ボックスの 自動きりかえ (ルビー・サファイア風): いまの ボックスが いっぱいなら つぎの あいている ボックスへ。レポートも かく
static bool8 TryJpBoxAutoSwitch(void)
{
    u8 cur, i, b;

    if ((gMain.vblankCounter2 & 15) != 0 || !FlagGet(FLAG_SYS_POKEMON_GET) || GetSafariZoneFlag()
     || QL_IS_PLAYBACK_STATE || ArePlayerFieldControlsLocked())
        return FALSE;
    cur = StorageGetCurrentBox();
    if (cur >= JP_BOXES || CountMonsInJpBox(cur) < IN_BOX_COUNT)
        return FALSE;
    for (i = 1; i < JP_BOXES; i++)
    {
        b = (cur + i) % JP_BOXES;
        if (CountMonsInJpBox(b) < IN_BOX_COUNT)
        {
            StringCopy(gStringVar1, GetBoxNamePtr(cur));
            StringCopy(gStringVar2, GetBoxNamePtr(b));
            SetCurrentBox(b);
            ScriptContext_SetupScript(EventScript_JpBoxSwitched);
            return TRUE;
        }
    }
    return FALSE;
}

// a full save stops a running script: the switch script ends first, then this task saves and starts the "saved" script
extern const u8 EventScript_JpBoxSaved[];
static void Task_JpAutoSave(u8 taskId)
{
    if (ScriptContext_IsEnabled())
        return;
    SaveMapView();
    IncrementGameStat(GAME_STAT_SAVED_GAME);
    TrySavingData(SAVE_NORMAL);
    ScriptContext_SetupScript(EventScript_JpBoxSaved);
    DestroyTask(taskId);
}

void JpAutoSaveGame(void)
{
    CreateTask(Task_JpAutoSave, 80);
}

// ProcessPlayerFieldInput (gunk/src/field_control_avatar.c) -> here (the bike gear toggle is already in Gunk's ProcessPlayerFieldInput)
// サファリゾーン: のこりの ほすうと ボールを 画面の したに (あるいている あいだ)
extern const u8 gJpText_SafariHud[];
void CB2_Overworld(void);
static const struct WindowTemplate sJpSafariHudWindow = {
    .bg = 0, .tilemapLeft = 1, .tilemapTop = 17, .width = 20, .height = 2, .paletteNum = 15, .baseBlock = 0x040
};

static void JpSafariHudPrint(u8 windowId)
{
    ConvertIntToDecimalStringN(gStringVar1, gSafariZoneStepCounter, STR_CONV_MODE_LEFT_ALIGN, 3);
    ConvertIntToDecimalStringN(gStringVar2, gNumSafariBalls, STR_CONV_MODE_LEFT_ALIGN, 2);
    StringExpandPlaceholders(gStringVar4, gJpText_SafariHud);
    FillWindowPixelBuffer(windowId, PIXEL_FILL(1));
    AddTextPrinterParameterized(windowId, FONT_NORMAL, gStringVar4, 2, 1, TEXT_SKIP_DRAW, NULL);
    CopyWindowToVram(windowId, COPYWIN_FULL);
}

static void Task_JpSafariHud(u8 taskId)
{
    s16 *data = gTasks[taskId].data;

    if (!GetSafariZoneFlag() || ArePlayerFieldControlsLocked() || gMain.callback2 != CB2_Overworld)
    {
        ClearStdWindowAndFrameToTransparent(data[0], TRUE);
        RemoveWindow(data[0]);
        DestroyTask(taskId);
        return;
    }
    if (data[1] != gSafariZoneStepCounter || data[2] != gNumSafariBalls)
    {
        data[1] = gSafariZoneStepCounter;
        data[2] = gNumSafariBalls;
        JpSafariHudPrint(data[0]);
    }
}

static void TryShowJpSafariHud(void)
{
    u8 taskId, windowId;

    if (!GetSafariZoneFlag() || FuncIsActiveTask(Task_JpSafariHud))
        return;
    windowId = AddWindow(&sJpSafariHudWindow);
    if (windowId == WINDOW_NONE)
        return;
    taskId = CreateTask(Task_JpSafariHud, 80);
    gTasks[taskId].data[0] = windowId;
    gTasks[taskId].data[1] = gSafariZoneStepCounter;
    gTasks[taskId].data[2] = gNumSafariBalls;
    LoadStdWindowFrameGfx();
    PutWindowTilemap(windowId);
    DrawStdWindowFrame(windowId, FALSE);
    JpSafariHudPrint(windowId);
}

bool8 JpFieldInputExtras(void)
{
    TryShowJpSafariHud();
    return TryJpBoxAutoSwitch();
}

// そだてや: いまの レベル -> gStringVar3
static void BufferDaycareLevel(struct BoxPokemon *mon, u32 steps)
{
    struct BoxPokemon temp = *mon;
    u32 exp = GetBoxMonData(&temp, MON_DATA_EXP) + steps;
    SetBoxMonData(&temp, MON_DATA_EXP, &exp);
    ConvertIntToDecimalStringN(gStringVar3, GetLevelFromBoxMonExp(&temp), STR_CONV_MODE_LEFT_ALIGN, 3);
}

void JpDaycareLevelRoute5(void)
{
    BufferDaycareLevel(&gSaveBlock1Ptr->route5DayCareMon.mon, gSaveBlock1Ptr->route5DayCareMon.steps);
}

void JpDaycareLevelFourIsland(void)
{
    struct DaycareMon *dm = &gSaveBlock1Ptr->daycare.mons[gSpecialVar_0x8004 & 1];
    BufferDaycareLevel(&dm->mon, dm->steps);
}

// 殿堂入りのたびに、捕まえていない伝説のポケモン (フリーザー・サンダー・ファイヤー・ミュウツー) が元の場所に戻る
static const u16 sLegends[][3] =
{
    {SPECIES_ARTICUNO, 0x082, 0x2BE},
    {SPECIES_ZAPDOS,   0x05D, 0x2BF},
    {SPECIES_MOLTRES,  0x052, 0x2BD},
    {SPECIES_MEWTWO,   0x081, 0x2BC},
};

void JpRespawnLegends(void)
{
    u8 i;
    for (i = 0; i < ARRAY_COUNT(sLegends); i++)
    {
        if (!GetSetPokedexFlag(SpeciesToNationalPokedexNum(sLegends[i][0]), FLAG_GET_CAUGHT))
        {
            FlagClear(sLegends[i][1]);
            FlagClear(sLegends[i][2]);
        }
    }
}
