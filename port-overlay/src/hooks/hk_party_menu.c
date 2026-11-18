#include "global.h"
#include "gflib.h"
#include "battle.h"
#include "battle_anim.h"
#include "battle_controllers.h"
#include "battle_gfx_sfx_util.h"
#include "battle_interface.h"
#include "battle_tower.h"
#include "berry_pouch.h"
#include "data.h"
#include "decompress.h"
#include "easy_chat.h"
#include "event_data.h"
#include "evolution_scene.h"
#include "field_effect.h"
#include "field_player_avatar.h"
#include "field_fadetransition.h"
#include "field_weather.h"
#include "fieldmap.h"
#include "fldeff.h"
#include "graphics.h"
#include "help_message.h"
#include "help_system.h"
#include "item.h"
#include "item_menu.h"
#include "item_use.h"
#include "link.h"
#include "link_rfu.h"
#include "load_save.h"
#include "mail.h"
#include "mail_data.h"
#include "main.h"
#include "menu.h"
#include "menu_helpers.h"
#include "new_menu_helpers.h"
#include "metatile_behavior.h"
#include "overworld.h"
#include "party_menu.h"
#include "player_pc.h"
#include "pokedex.h"
#include "pokemon.h"
#include "pokemon_icon.h"
#include "pokemon_jump.h"
#include "pokemon_special_anim.h"
#include "pokemon_summary_screen.h"
#include "quest_log.h"
#include "region_map.h"
#include "reshow_battle_screen.h"
#include "scanline_effect.h"
#include "script.h"
#include "start_menu.h"
#include "string_util.h"
#include "strings.h"
#include "task.h"
#include "teachy_tv.h"
#include "text_window.h"
#include "tm_case.h"
#include "trade.h"
#include "union_room.h"
#include "constants/battle.h"
#include "constants/easy_chat.h"
#include "constants/field_effects.h"
#include "constants/item_effects.h"
#include "constants/items.h"
#include "constants/maps.h"
#include "constants/moves.h"
#include "constants/pokemon.h"
#include "constants/quest_log.h"
#include "constants/songs.h"
#include "constants/sound.h"
#include "gunk_follower.h"

struct PartyMenuInternal
{
    TaskFunc task;
    MainCallback exitCallback;
    u32 chooseMultiple:1;
    u32 lastSelectedSlot:3;
    u32 spriteIdConfirmPokeball:7;
    u32 spriteIdCancelPokeball:7;
    u32 messageId:14;
    u8 windowId[3];
    u8 actions[8];
    u8 numActions;
    u16 palBuffer[BG_PLTT_SIZE / sizeof(u16)];
    s16 data[16];
};

enum
{
    CURSOR_OPTION_SUMMARY,
    CURSOR_OPTION_SWITCH,
    CURSOR_OPTION_CANCEL1,
    CURSOR_OPTION_ITEM,
    CURSOR_OPTION_GIVE,
    CURSOR_OPTION_TAKE_ITEM,
    CURSOR_OPTION_MAIL,
    CURSOR_OPTION_TAKE_MAIL,
    CURSOR_OPTION_READ,
    CURSOR_OPTION_CANCEL2,
    CURSOR_OPTION_SHIFT,
    CURSOR_OPTION_SEND_OUT,
    CURSOR_OPTION_ENTER,
    CURSOR_OPTION_NO_ENTRY,
    CURSOR_OPTION_STORE,
    CURSOR_OPTION_REGISTER,
    CURSOR_OPTION_TRADE1,
    CURSOR_OPTION_TRADE2,
    CURSOR_OPTION_GUNK_WALK,
    CURSOR_OPTION_GUNK_RETURN,
    CURSOR_OPTION_JP_FORGET,
    CURSOR_OPTION_FIELD_MOVES,
};

extern struct PartyMenuInternal *sPartyMenuInternal;
extern const u16 sFieldMoves[];
void PartyMenuRemoveWindow(u8 *windowId);
bool8 Gunk_CanUseHMMoveWithoutKnowing(struct Pokemon *mon, u16 move);
void Task_ClosePartyMenu(u8 taskId);

void SetPartyMonFieldSelectionActions(struct Pokemon *mons, u8 slotId)
{
    u8 i, j, numFieldMoves = 0, maxFieldMoves = MAX_MON_MOVES;

    sPartyMenuInternal->numActions = 0;
    AppendToList(sPartyMenuInternal->actions, &sPartyMenuInternal->numActions, CURSOR_OPTION_SUMMARY);
    if (IsFollowerPokemon(&mons[slotId]))
    {
        AppendToList(sPartyMenuInternal->actions, &sPartyMenuInternal->numActions, CURSOR_OPTION_GUNK_RETURN);
        maxFieldMoves--;
    }
    else if (Gunk_CanMonWalk(&mons[slotId]))
    {
        AppendToList(sPartyMenuInternal->actions, &sPartyMenuInternal->numActions, CURSOR_OPTION_GUNK_WALK);
        maxFieldMoves--;
    }
    // 赤フルカラー: forget any move (HMs included) from the party menu
    if (!GetMonData(&mons[slotId], MON_DATA_IS_EGG) && GetMonData(&mons[slotId], MON_DATA_MOVE2) != MOVE_NONE)
    {
        AppendToList(sPartyMenuInternal->actions, &sPartyMenuInternal->numActions, CURSOR_OPTION_JP_FORGET);
        maxFieldMoves--;
    }
    for (i = 0; i < MAX_MON_MOVES && numFieldMoves < maxFieldMoves; ++i)
    {
        for (j = 0; sFieldMoves[j] != FIELD_MOVE_END; ++j)
        {
            if (GetMonData(&mons[slotId], i + MON_DATA_MOVE1) == sFieldMoves[j])
            {
                AppendToList(sPartyMenuInternal->actions, &sPartyMenuInternal->numActions, j + CURSOR_OPTION_FIELD_MOVES);
                numFieldMoves++;
                break;
            }
        }
    }
    for (j = 0; j <= FIELD_MOVE_WATERFALL && numFieldMoves < maxFieldMoves; ++j)
    {
        if (!MonKnowsMove(&mons[slotId], sFieldMoves[j]) && Gunk_CanUseHMMoveWithoutKnowing(&mons[slotId], sFieldMoves[j]))
        {
            AppendToList(sPartyMenuInternal->actions, &sPartyMenuInternal->numActions, j + CURSOR_OPTION_FIELD_MOVES);
            numFieldMoves++;
        }
    }
    if (GetMonData(&mons[1], MON_DATA_SPECIES) != SPECIES_NONE)
        AppendToList(sPartyMenuInternal->actions, &sPartyMenuInternal->numActions, CURSOR_OPTION_SWITCH);
    if (ItemIsMail(GetMonData(&mons[slotId], MON_DATA_HELD_ITEM)))
        AppendToList(sPartyMenuInternal->actions, &sPartyMenuInternal->numActions, CURSOR_OPTION_MAIL);
    else
        AppendToList(sPartyMenuInternal->actions, &sPartyMenuInternal->numActions, CURSOR_OPTION_ITEM);
    AppendToList(sPartyMenuInternal->actions, &sPartyMenuInternal->numActions, CURSOR_OPTION_CANCEL1);
}

void CursorCB_GunkWalk(u8 taskId)
{
    PlaySE(SE_SELECT);
    PartyMenuRemoveWindow(&sPartyMenuInternal->windowId[0]);
    PartyMenuRemoveWindow(&sPartyMenuInternal->windowId[1]);
    Gunk_SetFollowerChoice(&gPlayerParty[gPartyMenu.slotId]);
    gPartyMenu.exitCallback = CB2_ReturnToField;
    Task_ClosePartyMenu(taskId);
}

void CursorCB_GunkReturn(u8 taskId)
{
    PlaySE(SE_SELECT);
    PartyMenuRemoveWindow(&sPartyMenuInternal->windowId[0]);
    PartyMenuRemoveWindow(&sPartyMenuInternal->windowId[1]);
    FlagSet(FLAG_GUNK_FOLLOWER_OFF);
    gPartyMenu.exitCallback = CB2_ReturnToField;
    Task_ClosePartyMenu(taskId);
}

extern const u8 JpEventScript_PartyForgetMove[];
static void JpForget_FieldCB(void)
{
    ScriptContext_SetupScript(JpEventScript_PartyForgetMove);
    ScriptContext_Stop();
    FieldCB_ContinueScriptHandleMusic();
}

static void CB2_JpForgetStart(void)
{
    ShowSelectMovePokemonSummaryScreen(gPlayerParty, gSpecialVar_0x8004, gPlayerPartyCount - 1, CB2_ReturnToField, 0);
    SetPokemonSummaryScreenMode(PSS_MODE_FORGET_MOVE);
    gFieldCallback = JpForget_FieldCB;
}

void CursorCB_JpForget(u8 taskId)
{
    PlaySE(SE_SELECT);
    PartyMenuRemoveWindow(&sPartyMenuInternal->windowId[0]);
    PartyMenuRemoveWindow(&sPartyMenuInternal->windowId[1]);
    gSpecialVar_0x8004 = gPartyMenu.slotId;
    gPartyMenu.exitCallback = CB2_JpForgetStart;
    Task_ClosePartyMenu(taskId);
}

const u8 gText_JpForget[] = _("わすれさせる");
const u8 gText_GunkWalk[] = _("つれあるく");
const u8 gText_GunkReturn[] = _("もどす");

// Japanese port: SELECT on a Pokémon in the field party menu makes it the one that walks (again: puts it away)
s8 *GetCurrentPartySlotPtr(void);
u8 PartyMenuButtonHandler(s8 *slotPtr);
void HandleChooseMonSelection(u8 taskId, s8 *slotPtr);
void HandleChooseMonCancel(u8 taskId, s8 *slotPtr);
void MoveCursorToConfirm(void);

static void SelectFollowerInPartyMenu(s8 slot)
{
    struct Pokemon *mon = &gPlayerParty[slot];

    if (!Gunk_CanMonWalk(mon))
    {
        PlaySE(SE_FAILURE);
        return;
    }
    if (IsFollowerPokemon(mon) && !FlagGet(FLAG_GUNK_FOLLOWER_OFF))
    {
        FlagSet(FLAG_GUNK_FOLLOWER_OFF);
        PlaySE(SE_BALL_OPEN);
    }
    else
    {
        Gunk_SetFollowerChoice(mon);
        PlayCry_Normal(GetMonData(mon, MON_DATA_SPECIES), 0);
    }
}

void Task_HandleChooseMonInput(u8 taskId)
{
    if (!gPaletteFade.active && MenuHelpers_ShouldWaitForLinkRecv() != TRUE)
    {
        s8 *slotPtr = GetCurrentPartySlotPtr();

        if (JOY_NEW(SELECT_BUTTON) && gPartyMenu.menuType == PARTY_MENU_TYPE_FIELD
         && gPartyMenu.action == PARTY_ACTION_CHOOSE_MON && *slotPtr >= 0 && *slotPtr < gPlayerPartyCount)
        {
            SelectFollowerInPartyMenu(*slotPtr);
            return;
        }
        switch (PartyMenuButtonHandler(slotPtr))
        {
        case A_BUTTON:
            HandleChooseMonSelection(taskId, slotPtr);
            break;
        case B_BUTTON:
            HandleChooseMonCancel(taskId, slotPtr);
            break;
        case START_BUTTON:
            if (sPartyMenuInternal->chooseMultiple)
            {
                PlaySE(SE_SELECT);
                MoveCursorToConfirm();
            }
            break;
        }
    }
}
