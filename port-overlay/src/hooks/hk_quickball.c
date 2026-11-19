#include "global.h"
#include "sprite.h"
#include "gflib.h"
#include "battle.h"
#include "battle_controllers.h"
#include "event_data.h"
#include "gunk_quick_ball.h"
#include "party_menu.h"
extern u16 gSpecialVar_ItemId;
#include "constants/songs.h"
// Japanese port of Gunk's Quick Run / Quick Ball hooks (src/battle_controller_player.c)
void PlayerBufferExecCompleted(void);
extern void (*gJpBattlerControllerFuncs[])(void);
void JpOpenBagAndChooseItem(void);

// first thing in HandleInputChooseAction after the bounce effects: TRUE = handled, return
bool8 JpQuickBall_Input(void)
{
    switch (Gunk_QuickBall_HandleInput())
    {
    case QUICK_BALL_CONSUMED:
        return TRUE;
    case QUICK_BALL_THROW:
        PlaySE(SE_SELECT);
        Gunk_QuickBall_Hide();
        BtlController_EmitTwoReturnValues(1, B_ACTION_USE_ITEM, 0);
        PlayerBufferExecCompleted();
        return TRUE;
    }
    if (JOY_NEW(R_BUTTON))
    {
        PlaySE(SE_SELECT);
        Gunk_QuickBall_Hide();
        BtlController_EmitTwoReturnValues(1, B_ACTION_RUN, 0);
        PlayerBufferExecCompleted();
        return TRUE;
    }
    /* A ends the action menu. B doesn't in a single battle (it only cancels the partner's choice in a double
       battle, where the widget isn't shown), so B leaves the widget on screen */
    if (JOY_NEW(A_BUTTON))
        Gunk_QuickBall_Hide();
    return FALSE;
}

void PlayerHandleChooseItem(void)
{
    s32 i;
    u16 ball;

    if (Gunk_QuickBall_TakePending(&ball))
    {
        gBattlerInMenuId = gActiveBattler;
        for (i = 0; i < 3; ++i)
            gBattlePartyCurrentOrder[i] = gBattleBufferA[gActiveBattler][1 + i];
        gSpecialVar_ItemId = ball;
        BtlController_EmitOneReturnValue(1, ball);
        PlayerBufferExecCompleted();
        return;
    }
    BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 0x10, RGB_BLACK);
    gJpBattlerControllerFuncs[gActiveBattler] = JpOpenBagAndChooseItem;
    gBattlerInMenuId = gActiveBattler;
    for (i = 0; i < 3; ++i)
        gBattlePartyCurrentOrder[i] = gBattleBufferA[gActiveBattler][1 + i];
}

void CompleteWhenChoseItem(void)
{
    if (gMain.callback2 == BattleMainCB2 && !gPaletteFade.active)
    {
        Gunk_QuickBall_NoteItemUsed(gSpecialVar_ItemId);
        BtlController_EmitOneReturnValue(1, gSpecialVar_ItemId);
        PlayerBufferExecCompleted();
    }
}
