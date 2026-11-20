#include "global.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "field_control_avatar.h"
#include "field_player_avatar.h"
#include "field_specials.h"
#include "field_weather.h"
#include "fieldmap.h"
#include "item_menu.h"
#include "link.h"
#include "metatile_behavior.h"
#include "overworld.h"
#include "palette.h"
#include "party_menu.h"
#include "quest_log.h"
#include "script.h"
#include "sound.h"
#include "task.h"
#include "bike.h"
#include "constants/flags.h"
#include "constants/items.h"
#include "constants/item_menu.h"
#include "constants/songs.h"

// フィールドで L＝てもちの ポケモン、R＝バッグ（ヘルプ・Rの とうろく の かわり）。
// とじると スタートメニューは ださずに そのまま フィールドへ もどる。

#define VAR_GUNK_REGISTERED_ITEM_2 0x402A

void DestroySafariZoneStatsWindow(void);

static void CB2_JpPartyFromL(void)
{
    CB2_PartyMenuFromStartMenu();
    gPartyMenu.exitCallback = CB2_ReturnToField;
}

static void CB2_JpBagFromR(void)
{
    GoToBagMenu(ITEMMENULOCATION_FIELD, OPEN_BAG_LAST, CB2_ReturnToField);
}

static void Task_JpFieldLR(u8 taskId)
{
    if (gPaletteFade.active)
        return;
    PlayRainStoppingSoundEffect();
    DestroySafariZoneStatsWindow();
    CleanupOverworldWindowsAndTilemaps();
    SetMainCallback2(gTasks[taskId].data[0] == 1 ? CB2_JpPartyFromL : CB2_JpBagFromR);
    DestroyTask(taskId);
}

static bool8 CanPressFieldButtons(void)
{
    u8 tts = gPlayerAvatar.tileTransitionState;
    s16 x, y;
    bool8 forced;

    PlayerGetDestCoords(&x, &y);
    forced = MetatileBehavior_IsForcedMovementTile(MapGridGetMetatileBehaviorAt(x, y));

    if (!((tts == T_TILE_CENTER && !forced) || tts == T_NOT_MOVING))
        return FALSE;
    if (GetPlayerSpeed() == PLAYER_SPEED_FASTEST)
        return FALSE;
    if (QL_IS_PLAYBACK_STATE)
        return FALSE;
    if (gPlayerAvatar.flags & PLAYER_AVATAR_FLAG_FORCED)
        return FALSE;
    return TRUE;
}

bool8 JpFieldLRMenu(struct FieldInput *input)
{
    u8 which = 0;

    if (input->pressedRButton)
        which = 2;
    else if (JOY_NEW(L_BUTTON) && gSaveBlock2Ptr->optionsButtonMode != OPTIONS_BUTTON_MODE_L_EQUALS_A && CanPressFieldButtons())
        which = 1;
    if (which == 0)
        return FALSE;
    if (InUnionRoom() == TRUE)
        return FALSE;
    if (which == 1 && !FlagGet(FLAG_SYS_POKEMON_GET))
        return FALSE;

    VarSet(VAR_GUNK_REGISTERED_ITEM_2, ITEM_NONE);   // the old "R" registration is gone
    PlaySE(SE_WIN_OPEN);
    FreezeObjectEvents();
    HandleEnforcedLookDirectionOnPlayerStopMoving();
    StopPlayerAvatar();
    LockPlayerFieldControls();
    FadeScreen(FADE_TO_BLACK, 0);
    gTasks[CreateTask(Task_JpFieldLR, 80)].data[0] = which;
    return TRUE;
}
