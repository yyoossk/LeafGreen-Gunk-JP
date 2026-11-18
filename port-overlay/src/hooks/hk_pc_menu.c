#include "global.h"
#include "event_data.h"
#include "constants/flags.h"
// Gunk's PC menu with a わざおしえ row, written against the Japanese CreatePCMenuWindow (JP 0x0809C9F0)

u8 JpGetMenuCursorDimensionByFont(u8 font, u8 which);
u16 JpGetStringTilesWide(const u8 *str);
u8 JpCreateWindowFromRect(u8 x, u8 y, u8 w, u8 h);
void JpSetStdWindowBorderStyle(u8 windowId, bool8 copyToVram);
u16 JpAddTextPrinterParameterized(u8 windowId, u8 fontId, const u8 *str, u8 x, u8 y, u8 speed, void *callback);
u8 *JpStringExpandPlaceholders(u8 *dest, const u8 *src);
void JpMenu_PrintFormatIntlPlayerName(u8 windowId, const u8 *src, u16 x, u16 y);
u8 JpMenu_InitCursor(u8 windowId, u8 fontId, u8 left, u8 top, u8 cursorHeight, u8 numChoices, u8 initialCursorPos);
void JpCreateMCMenuInputHandlerTask(bool8 ignoreBPress, u8 count, u8 windowId, u8 mcId);
void JpScheduleBgCopyTilemapToVram(u8 bg);
bool8 JpFlagGet(u16 id);

#define JP_FONT_NORMAL 2
#define JP_STRVAR4 ((u8 *)0x02021C88)
#define JpText_BillSPc     ((const u8 *)0x083DA21C)
#define JpText_SomeoneSPc  ((const u8 *)0x083DA213)
#define JpText_SPc         ((const u8 *)0x083DA225)
#define JpText_HallOfFame  ((const u8 *)0x083DA22D)
#define JpText_LogOff      ((const u8 *)0x083DA234)
#define JpText_ProfOakSPc  ((const u8 *)0x083DA23C)

enum {
    PC_ACTION_STORAGE,
    PC_ACTION_PLAYER,
    PC_ACTION_OAK,
    PC_ACTION_HALL_OF_FAME,
    PC_ACTION_LOG_OFF,
    PC_ACTION_MOVE_TUTOR,
};
#define PC_MENU_MAX_ROWS 6

static const u8 sJpText_GunkMoveTutor[] = _("わざおしえ");

static u8 GetPCMenuActions(u8 *actions)
{
    u8 buf[PC_MENU_MAX_ROWS];
    u8 n = 0;

    if (actions == NULL)
        actions = buf;
    actions[n++] = PC_ACTION_STORAGE;
    actions[n++] = PC_ACTION_PLAYER;
    if (JpFlagGet(FLAG_SYS_GAME_CLEAR) || JpFlagGet(FLAG_SYS_POKEDEX_GET))
        actions[n++] = PC_ACTION_OAK;
    if (JpFlagGet(FLAG_SYS_GAME_CLEAR))
        actions[n++] = PC_ACTION_HALL_OF_FAME;
    actions[n++] = PC_ACTION_MOVE_TUTOR;
    actions[n++] = PC_ACTION_LOG_OFF;
    return n;
}

void Gunk_TranslatePCMenuResult(void)
{
    u8 actions[PC_MENU_MAX_ROWS];
    u8 n = GetPCMenuActions(actions);

    if (gSpecialVar_Result < n)
        gSpecialVar_Result = actions[gSpecialVar_Result];
}

void JpCreatePCMenuWindow(void)
{
    u8 cursorWidth = JpGetMenuCursorDimensionByFont(JP_FONT_NORMAL, 0) + 1;
    u8 windowWidth;
    u8 numItems;
    u8 windowId;
    u8 actions[PC_MENU_MAX_ROWS];
    u8 i;
    u16 w;

    JpGetMenuCursorDimensionByFont(JP_FONT_NORMAL, 1);
    w = JpGetStringTilesWide(JpText_SPc);
    if (w == 9 || w == 10)
        windowWidth = 14;
    else if (JpFlagGet(FLAG_SYS_POKEDEX_GET))
        windowWidth = 14;
    else
        windowWidth = 13;

    numItems = GetPCMenuActions(actions);
    windowId = JpCreateWindowFromRect(0, 0, windowWidth, numItems * 2);
    JpSetStdWindowBorderStyle(windowId, FALSE);
    for (i = 2; i < numItems; i++)
    {
        const u8 *str;
        switch (actions[i])
        {
        case PC_ACTION_OAK:          str = JpText_ProfOakSPc; break;
        case PC_ACTION_HALL_OF_FAME: str = JpText_HallOfFame; break;
        case PC_ACTION_MOVE_TUTOR:   str = sJpText_GunkMoveTutor; break;
        default:                     str = JpText_LogOff; break;
        }
        JpAddTextPrinterParameterized(windowId, JP_FONT_NORMAL, str, cursorWidth, 2 + 16 * i, 0xFF, NULL);
    }
    if (JpFlagGet(FLAG_SYS_NOT_SOMEONES_PC))
        JpAddTextPrinterParameterized(windowId, JP_FONT_NORMAL, JpText_BillSPc, cursorWidth, 2, 0xFF, NULL);
    else
        JpAddTextPrinterParameterized(windowId, JP_FONT_NORMAL, JpText_SomeoneSPc, cursorWidth, 2, 0xFF, NULL);
    JpStringExpandPlaceholders(JP_STRVAR4, JpText_SPc);
    JpMenu_PrintFormatIntlPlayerName(windowId, JP_STRVAR4, cursorWidth, 18);
    JpMenu_InitCursor(windowId, JP_FONT_NORMAL, 0, 2, 16, numItems, 0);
    JpCreateMCMenuInputHandlerTask(FALSE, numItems, windowId, 0xFF);
    JpScheduleBgCopyTilemapToVram(0);
}
