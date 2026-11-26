#include "global.h"
#include "event_data.h"
#include "string_util.h"
#include "task.h"
#include "list_menu.h"
#include "window.h"
#include "sound.h"
#include "malloc.h"
#include "script.h"
#include "menu_indicators.h"
#include "constants/moves.h"
#include "constants/songs.h"

// 殿堂入りの あとの「わざおしえ マスター」（タマムシデパート 2かい）：
// おしえわざ 18こ（ふつうの 15こ ＋ ハードプラント・ブラストバーン・ハイドロカノン）を ぜんぶ、なんどでも ただで おしえる

u8 JpCreateWindowFromRect(u8 x, u8 y, u8 w, u8 h);
void JpSetStdWindowBorderStyle(u8 windowId, bool8 copyToVram);
void JpScheduleBgCopyTilemapToVram(u8 bg);
void ClearStdWindowAndFrameToTransparent(u8 windowId, bool8 copyToVram);
// JP の わざの なまえ（1つ 8バイト）
#define sJpMoveNames ((const u8 (*)[8])0x081FFE54)
#define JP_FONT_NORMAL 2

#define TUTOR_COUNT 18
#define ROWS 6
#define TUTOR_CANCEL 0xFF

// VAR_0x8005（おしえわざの ばんごう）の じゅんに ならべる
static const u16 sTutorAllMoves[TUTOR_COUNT] = {
    MOVE_MEGA_PUNCH, MOVE_SWORDS_DANCE, MOVE_MEGA_KICK, MOVE_BODY_SLAM, MOVE_DOUBLE_EDGE, MOVE_COUNTER,
    MOVE_SEISMIC_TOSS, MOVE_MIMIC, MOVE_METRONOME, MOVE_SOFT_BOILED, MOVE_DREAM_EATER, MOVE_THUNDER_WAVE,
    MOVE_EXPLOSION, MOVE_ROCK_SLIDE, MOVE_SUBSTITUTE, MOVE_FRENZY_PLANT, MOVE_BLAST_BURN, MOVE_HYDRO_CANNON,
};
static const u8 sText_TutorAllCancel[] = _("やめる");

static EWRAM_DATA struct ListMenuItem *sTutorAllItems = NULL;
static EWRAM_DATA u16 sTutorAllScroll = 0;
static EWRAM_DATA u16 sTutorAllCursor = 0;

static void Task_TutorAllMenu(u8 taskId)
{
    s16 *data = gTasks[taskId].data;
    s32 input = ListMenu_ProcessInput(data[0]);

    ListMenuGetScrollAndRow(data[0], &sTutorAllScroll, &sTutorAllCursor);
    if (input == LIST_NOTHING_CHOSEN)
        return;
    PlaySE(SE_SELECT);
    if (data[2] != 0xFF)
        RemoveScrollIndicatorArrowPair(data[2]);
    gSpecialVar_Result = (input == LIST_CANCEL) ? TUTOR_CANCEL : input;
    DestroyListMenuTask(data[0], NULL, NULL);
    ClearStdWindowAndFrameToTransparent(data[1], TRUE);
    RemoveWindow(data[1]);
    Free(sTutorAllItems);
    sTutorAllItems = NULL;
    DestroyTask(taskId);
    ScriptContext_Enable();
}

// VAR_RESULT ← えらんだ おしえわざの ばんごう（0〜17）、やめる・B は 0xFF
void JpTutorAll_Menu(void)
{
    struct ListMenuTemplate t = {0};
    u8 windowId, taskId, i;

    if (gSpecialVar_Result != 0xFFFE)   // はじめて ひらく ときは カーソルを いちばん うえに
        sTutorAllScroll = sTutorAllCursor = 0;
    sTutorAllItems = Alloc(sizeof(struct ListMenuItem) * (TUTOR_COUNT + 1));
    for (i = 0; i < TUTOR_COUNT; i++)
    {
        sTutorAllItems[i].label = sJpMoveNames[sTutorAllMoves[i]];
        sTutorAllItems[i].index = i;
    }
    sTutorAllItems[TUTOR_COUNT].label = sText_TutorAllCancel;
    sTutorAllItems[TUTOR_COUNT].index = TUTOR_CANCEL;

    windowId = JpCreateWindowFromRect(17, 1, 12, ROWS * 2);
    JpSetStdWindowBorderStyle(windowId, FALSE);
    t.items = sTutorAllItems;
    t.totalItems = TUTOR_COUNT + 1;
    t.maxShowed = ROWS;
    t.windowId = windowId;
    t.item_X = 8;
    t.cursor_X = 0;
    t.upText_Y = 0;
    t.cursorPal = 2;
    t.fillValue = 1;
    t.cursorShadowPal = 3;
    t.fontId = JP_FONT_NORMAL;
    t.scrollMultiple = LIST_MULTIPLE_SCROLL_DPAD;

    taskId = CreateTask(Task_TutorAllMenu, 80);
    gTasks[taskId].data[1] = windowId;
    gTasks[taskId].data[0] = ListMenuInit(&t, sTutorAllScroll, sTutorAllCursor);
    gTasks[taskId].data[2] = AddScrollIndicatorArrowPairParameterized(SCROLL_ARROW_UP, 17 * 8 + 12 * 4, 8, 8 + ROWS * 16,
                                 TUTOR_COUNT + 1 - ROWS, 111, 111, &sTutorAllScroll);
    CopyWindowToVram(windowId, COPYWIN_FULL);
    JpScheduleBgCopyTilemapToVram(0);
}

// STR_VAR_1 ← VAR_0x8005 の おしえわざの なまえ
void JpTutorAll_BufferMove(void)
{
    u16 i = gSpecialVar_0x8005;
    if (i < TUTOR_COUNT)
        StringCopy(gStringVar1, sJpMoveNames[sTutorAllMoves[i]]);
}
