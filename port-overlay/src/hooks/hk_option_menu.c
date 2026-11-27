#include "global.h"
#include "gflib.h"
#include "scanline_effect.h"
#include "text_window_graphics.h"
#include "menu.h"
#include "task.h"
#include "overworld.h"
#include "help_system.h"
#include "text_window.h"
#include "strings.h"
#include "field_fadetransition.h"
#include "gba/m4a_internal.h"

// 「せってい」に「かいふく アニメ」(みる／みない) を追加し、「おわる」をなくした、ファイアレッドの option_menu.c の作り直し
// （ファイアレッド改良パッチの hk_option_menu.c から。リーフグリーンの アドレス。「けいけんち ぶんぱい」の 行は まだ ない）。
// A／B で とじる。
// JP CB2_OptionsMenuFromStartMenu (0x08087ED0) is replaced by JpCB2_OptionsMenuFromStartMenu (tramp in patch_port.py).
// 7 rows with the original 13px pitch.

bool32 IsActiveOverworldLinkBusy(void);

enum
{
    MENUITEM_TEXTSPEED = 0,
    MENUITEM_BATTLESCENE,
    MENUITEM_BATTLESTYLE,
    MENUITEM_SOUND,
    MENUITEM_BUTTONMODE,
    MENUITEM_FRAMETYPE,
    MENUITEM_FASTHEAL,
    MENUITEM_UNSEEN,
    MENUITEM_COUNT
};

struct JpOptionMenu
{
    u16 option[MENUITEM_COUNT];
    u16 cursorPos;
    u8 loadState;
    u8 state;
    u8 loadPaletteState;
};

#define sOptionMenuPtr (*(struct JpOptionMenu **)0x0203956C)   // JP sOptionMenuPtr (EWRAM)

#define ROW_PITCH 12
#define ROW_Y(i) ((i) * ROW_PITCH)

// JP data
#define JpBgTemplates       ((const struct BgTemplate *)0x0838E784)
#define JpOptionMenuPalette ((const u16 *)0x0838E790)
#define JpTextColor         ((const u8 *)0x0838E80F)
#define JpText_Option       ((const u8 *)0x083DBB10)
#define JpText_FrameType    ((const u8 *)0x083DBB82)

extern const u8 gJpText_TextSpeedInstant[];
extern const u8 gJpText_OptionFastHeal[];
extern const u8 gJpText_OptionUnseen[];
extern const u8 gJpText_UnseenHide[];
extern const u8 gJpText_UnseenShow[];
bool8 FlagGet(u16 id);
u8 FlagSet(u16 id);
u8 FlagClear(u16 id);
#define FLAG_JP_HERE_SHOW_UNSEEN 0x4AC   // ここででるポケモン：まだ みていない ポケモンも なまえを だす
#define FLAG_JP_FAST_HEAL 0x4AB   // ポケモンセンターの かいふく アニメを みない

static const u16 sItemCounts[MENUITEM_COUNT] = {4, 2, 2, 2, 3, 10, 2, 2};

static const u8 *const sItemNames[MENUITEM_COUNT] =
{
    (const u8 *)0x083DBB1A, (const u8 *)0x083DBB23, (const u8 *)0x083DBB2C, (const u8 *)0x083DBB35,
    (const u8 *)0x083DBB3A, (const u8 *)0x083DBB41, gJpText_OptionFastHeal, gJpText_OptionUnseen,
};
static const u8 *const sTextSpeedNames[] = {(const u8 *)0x083DBB4B, (const u8 *)0x083DBB4F, (const u8 *)0x083DBB53, gJpText_TextSpeedInstant};
static const u8 *const sSeeNames[] = {(const u8 *)0x083DBB57, (const u8 *)0x083DBB5B};   // みる／みない
static const u8 *const sStyleNames[] = {(const u8 *)0x083DBB5F, (const u8 *)0x083DBB64};
static const u8 *const sUnseenNames[] = {gJpText_UnseenHide, gJpText_UnseenShow};
static const u8 *const sSoundNames[] = {(const u8 *)0x083DBB69, (const u8 *)0x083DBB6E};
static const u8 *const sButtonNames[] = {(const u8 *)0x083DBB77, (const u8 *)0x083DBB7F, (const u8 *)0x083DBB7B};

static const struct WindowTemplate sWinTemplates[] =
{
    { .bg = 1, .tilemapLeft = 2, .tilemapTop = 3, .width = 26, .height = 2, .paletteNum = 1, .baseBlock = 2 },
    { .bg = 0, .tilemapLeft = 2, .tilemapTop = 7, .width = 26, .height = 12, .paletteNum = 1, .baseBlock = 0x36 },
    { .bg = 2, .tilemapLeft = 0, .tilemapTop = 0, .width = 30, .height = 2, .paletteNum = 15, .baseBlock = 0x16e },
    DUMMY_WIN_TEMPLATE
};

static void JpCB2_InitOptionMenu(void);
static void JpCB2_OptionMenu(void);
static void JpTask_OptionMenu(u8 taskId);

static void JpCB2_InitOptionMenu(void)
{
    RunTasks();
    AnimateSprites();
    BuildOamBuffer();
    UpdatePaletteFade();
}

static void JpVBlankCB_OptionMenu(void)
{
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

void JpCB2_OptionsMenuFromStartMenu(void)
{
    u8 i;

    if (gMain.savedCallback == NULL)
        gMain.savedCallback = CB2_ReturnToFieldWithOpenMenu;
    sOptionMenuPtr = AllocZeroed(sizeof(struct JpOptionMenu));
    sOptionMenuPtr->loadState = 0;
    sOptionMenuPtr->loadPaletteState = 0;
    sOptionMenuPtr->state = 0;
    sOptionMenuPtr->cursorPos = 0;
    sOptionMenuPtr->option[MENUITEM_TEXTSPEED] = gSaveBlock2Ptr->optionsTextSpeed;
    sOptionMenuPtr->option[MENUITEM_BATTLESCENE] = gSaveBlock2Ptr->optionsBattleSceneOff;
    sOptionMenuPtr->option[MENUITEM_BATTLESTYLE] = gSaveBlock2Ptr->optionsBattleStyle;
    sOptionMenuPtr->option[MENUITEM_SOUND] = gSaveBlock2Ptr->optionsSound;
    sOptionMenuPtr->option[MENUITEM_BUTTONMODE] = gSaveBlock2Ptr->optionsButtonMode;
    sOptionMenuPtr->option[MENUITEM_FRAMETYPE] = gSaveBlock2Ptr->optionsWindowFrameType;
    sOptionMenuPtr->option[MENUITEM_FASTHEAL] = FlagGet(FLAG_JP_FAST_HEAL) ? 1 : 0;
    sOptionMenuPtr->option[MENUITEM_UNSEEN] = FlagGet(FLAG_JP_HERE_SHOW_UNSEEN) ? 1 : 0;
    for (i = 0; i < MENUITEM_COUNT; i++)
    {
        if (sOptionMenuPtr->option[i] > sItemCounts[i] - 1)
            sOptionMenuPtr->option[i] = 0;
    }
    SetHelpContext(HELPCONTEXT_OPTIONS);
    SetMainCallback2(JpCB2_OptionMenu);
}

static void InitOptionMenuBg(void)
{
    void *dest = (void *)VRAM;
    DmaClearLarge16(3, dest, VRAM_SIZE, 0x1000);
    DmaClear32(3, (void *)OAM, OAM_SIZE);
    DmaClear16(3, (void *)PLTT, PLTT_SIZE);
    SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_0);
    ResetBgsAndClearDma3BusyFlags(0);
    InitBgsFromTemplates(0, JpBgTemplates, 3);
    ChangeBgX(0, 0, 0);
    ChangeBgY(0, 0, 0);
    ChangeBgX(1, 0, 0);
    ChangeBgY(1, 0, 0);
    ChangeBgX(2, 0, 0);
    ChangeBgY(2, 0, 0);
    ChangeBgX(3, 0, 0);
    ChangeBgY(3, 0, 0);
    InitWindows(sWinTemplates);
    DeactivateAllTextPrinters();
    SetGpuReg(REG_OFFSET_BLDCNT, BLDCNT_TGT1_BG0 | BLDCNT_EFFECT_BLEND | BLDCNT_EFFECT_LIGHTEN);
    SetGpuReg(REG_OFFSET_BLDY, BLDCNT_TGT1_BG1);
    SetGpuReg(REG_OFFSET_WININ, WININ_WIN0_BG0);
    SetGpuReg(REG_OFFSET_WINOUT, WINOUT_WIN01_BG0 | WINOUT_WIN01_BG1 | WINOUT_WIN01_BG2 | WINOUT_WIN01_CLR);
    SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_OBJ_1D_MAP | DISPCNT_OBJ_ON | DISPCNT_WIN0_ON);
    ShowBg(0);
    ShowBg(1);
    ShowBg(2);
}

static bool8 LoadOptionMenuPalette(void)
{
    switch (sOptionMenuPtr->loadPaletteState)
    {
    case 0:
        LoadBgTiles(1, GetUserWindowGraphics(sOptionMenuPtr->option[MENUITEM_FRAMETYPE])->tiles, 0x120, 0x1AA);
        break;
    case 1:
        LoadPalette(GetUserWindowGraphics(sOptionMenuPtr->option[MENUITEM_FRAMETYPE])->palette, BG_PLTT_ID(2), PLTT_SIZE_4BPP);
        break;
    case 2:
        LoadPalette(JpOptionMenuPalette, BG_PLTT_ID(1), 0x20);
        LoadPalette(GetTextWindowPalette(2), BG_PLTT_ID(15), PLTT_SIZE_4BPP);
        break;
    case 3:
        LoadStdWindowGfxOnBg(1, 0x1B3, BG_PLTT_ID(3));
        break;
    default:
        return TRUE;
    }
    sOptionMenuPtr->loadPaletteState++;
    return FALSE;
}

static void PrintOptionMenuHeader(void)
{
    FillWindowPixelBuffer(0, PIXEL_FILL(1));
    AddTextPrinterParameterized(0, FONT_NORMAL, JpText_Option, 8, 1, TEXT_SKIP_DRAW, NULL);
    PutWindowTilemap(0);
    CopyWindowToVram(0, COPYWIN_FULL);
}

static void DrawOptionMenuBg(void)
{
    u8 h = 2;
    FillBgTilemapBufferRect(1, 0x1B3, 1, 2, 1, 1, 3);
    FillBgTilemapBufferRect(1, 0x1B4, 2, 2, 0x1B, 1, 3);
    FillBgTilemapBufferRect(1, 0x1B5, 0x1C, 2, 1, 1, 3);
    FillBgTilemapBufferRect(1, 0x1B6, 1, 3, 1, h, 3);
    FillBgTilemapBufferRect(1, 0x1B8, 0x1C, 3, 1, h, 3);
    FillBgTilemapBufferRect(1, 0x1B9, 1, 5, 1, 1, 3);
    FillBgTilemapBufferRect(1, 0x1BA, 2, 5, 0x1B, 1, 3);
    FillBgTilemapBufferRect(1, 0x1BB, 0x1C, 5, 1, 1, 3);
    FillBgTilemapBufferRect(1, 0x1AA, 1, 6, 1, 1, h);
    FillBgTilemapBufferRect(1, 0x1AB, 2, 6, 0x1A, 1, h);
    FillBgTilemapBufferRect(1, 0x1AC, 0x1C, 6, 1, 1, h);
    FillBgTilemapBufferRect(1, 0x1AD, 1, 7, 1, 0x10, h);
    FillBgTilemapBufferRect(1, 0x1AF, 0x1C, 7, 1, 0x10, h);
    FillBgTilemapBufferRect(1, 0x1B0, 1, 0x13, 1, 1, h);
    FillBgTilemapBufferRect(1, 0x1B1, 2, 0x13, 0x1A, 1, h);
    FillBgTilemapBufferRect(1, 0x1B2, 0x1C, 0x13, 1, 1, h);
    CopyBgTilemapBufferToVram(1);
}

static void LoadOptionMenuItemNames(void)
{
    u8 i;
    FillWindowPixelBuffer(1, PIXEL_FILL(1));
    for (i = 0; i < MENUITEM_COUNT; i++)
        AddTextPrinterParameterized(1, FONT_NORMAL, sItemNames[i], 8, ROW_Y(i), TEXT_SKIP_DRAW, NULL);
}

static void BufferOptionMenuString(u8 selection)
{
    u8 str[20];
    u8 buf[12];
    u8 dst[3];
    u8 x, y;
    const u8 *s = NULL;
    u16 v = sOptionMenuPtr->option[selection];

    memcpy(dst, JpTextColor, 3);
    x = 0x82;
    y = ROW_Y(selection);
    FillWindowPixelRect(1, 1, x, y, 0x46, ROW_PITCH);

    switch (selection)
    {
    case MENUITEM_TEXTSPEED:   s = sTextSpeedNames[v]; break;
    case MENUITEM_BATTLESCENE: s = sSeeNames[v]; break;
    case MENUITEM_BATTLESTYLE: s = sStyleNames[v]; break;
    case MENUITEM_SOUND:       s = sSoundNames[v]; break;
    case MENUITEM_BUTTONMODE:  s = sButtonNames[v]; break;
    case MENUITEM_FASTHEAL:    s = sSeeNames[v]; break;
    case MENUITEM_UNSEEN:      s = sUnseenNames[v]; break;
    case MENUITEM_FRAMETYPE:
        StringCopy(str, JpText_FrameType);
        ConvertIntToDecimalStringN(buf, v + 1, 1, 2);
        StringAppendN(str, buf, 3);
        s = str;
        break;
    }
    if (s != NULL)
        AddTextPrinterParameterized3(1, FONT_NORMAL, x, y, dst, -1, s);
    PutWindowTilemap(1);
    CopyWindowToVram(1, COPYWIN_FULL);
}

static void UpdateSettingSelectionDisplay(u16 selection)
{
    u16 y = 0x38 + ROW_Y(selection);
    SetGpuReg(REG_OFFSET_WIN0V, WIN_RANGE(y, y + ROW_PITCH));
    SetGpuReg(REG_OFFSET_WIN0H, WIN_RANGE(0x10, 0xE0));
}

static void JpCB2_OptionMenu(void)
{
    u8 i;
    switch (sOptionMenuPtr->state)
    {
    case 0:
        SetVBlankCallback(NULL);
        SetHBlankCallback(NULL);
        break;
    case 1:
        InitOptionMenuBg();
        break;
    case 2:
        ResetSpriteData();
        ResetPaletteFade();
        FreeAllSpritePalettes();
        ResetTasks();
        ScanlineEffect_Stop();
        break;
    case 3:
        if (LoadOptionMenuPalette() != TRUE)
            return;
        break;
    case 4:
        PrintOptionMenuHeader();
        break;
    case 5:
        DrawOptionMenuBg();
        break;
    case 6:
        LoadOptionMenuItemNames();
        break;
    case 7:
        for (i = 0; i < MENUITEM_COUNT; i++)
            BufferOptionMenuString(i);
        break;
    case 8:
        UpdateSettingSelectionDisplay(sOptionMenuPtr->cursorPos);
        break;
    default:
        CreateTask(JpTask_OptionMenu, 0);
        SetMainCallback2(JpCB2_InitOptionMenu);
        break;
    }
    sOptionMenuPtr->state++;
}

static u8 OptionMenu_ProcessInput(void)
{
    u16 cur = sOptionMenuPtr->cursorPos;
    u16 *opt = &sOptionMenuPtr->option[cur];

    if (JOY_REPT(DPAD_RIGHT))
    {
        if (sItemCounts[cur] == 0)
            return 0;
        *opt = (*opt == sItemCounts[cur] - 1) ? 0 : *opt + 1;
        return cur == MENUITEM_FRAMETYPE ? 2 : 4;
    }
    else if (JOY_REPT(DPAD_LEFT))
    {
        if (sItemCounts[cur] == 0)
            return 0;
        *opt = (*opt == 0) ? sItemCounts[cur] - 1 : *opt - 1;
        return cur == MENUITEM_FRAMETYPE ? 2 : 4;
    }
    else if (JOY_REPT(DPAD_UP))
    {
        sOptionMenuPtr->cursorPos = (cur == 0) ? MENUITEM_COUNT - 1 : cur - 1;
        return 3;
    }
    else if (JOY_REPT(DPAD_DOWN))
    {
        sOptionMenuPtr->cursorPos = (cur == MENUITEM_COUNT - 1) ? 0 : cur + 1;
        return 3;
    }
    else if (JOY_NEW(B_BUTTON) || JOY_NEW(A_BUTTON))
    {
        return 1;
    }
    return 0;
}

static void CloseAndSaveOptionMenu(u8 taskId)
{
    gFieldCallback = FieldCB_DefaultWarpExit;
    SetMainCallback2(gMain.savedCallback);
    FreeAllWindowBuffers();
    gSaveBlock2Ptr->optionsTextSpeed = sOptionMenuPtr->option[MENUITEM_TEXTSPEED];
    gSaveBlock2Ptr->optionsBattleSceneOff = sOptionMenuPtr->option[MENUITEM_BATTLESCENE];
    gSaveBlock2Ptr->optionsBattleStyle = sOptionMenuPtr->option[MENUITEM_BATTLESTYLE];
    gSaveBlock2Ptr->optionsSound = sOptionMenuPtr->option[MENUITEM_SOUND];
    gSaveBlock2Ptr->optionsButtonMode = sOptionMenuPtr->option[MENUITEM_BUTTONMODE];
    gSaveBlock2Ptr->optionsWindowFrameType = sOptionMenuPtr->option[MENUITEM_FRAMETYPE];
    if (sOptionMenuPtr->option[MENUITEM_FASTHEAL] == 1)
        FlagSet(FLAG_JP_FAST_HEAL);
    else
        FlagClear(FLAG_JP_FAST_HEAL);
    if (sOptionMenuPtr->option[MENUITEM_UNSEEN] == 1)
        FlagSet(FLAG_JP_HERE_SHOW_UNSEEN);
    else
        FlagClear(FLAG_JP_HERE_SHOW_UNSEEN);
    SetPokemonCryStereo(gSaveBlock2Ptr->optionsSound);
    Free(sOptionMenuPtr);
    sOptionMenuPtr = NULL;
    DestroyTask(taskId);
}

static void JpTask_OptionMenu(u8 taskId)
{
    switch (sOptionMenuPtr->loadState)
    {
    case 0:
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0x10, 0, RGB_BLACK);
        SetVBlankCallback(JpVBlankCB_OptionMenu);
        sOptionMenuPtr->loadState++;
        break;
    case 1:
        if (gPaletteFade.active)
            return;
        sOptionMenuPtr->loadState++;
        break;
    case 2:
        if (((bool32)IsActiveOverworldLinkBusy()) == TRUE)
            break;
        switch (OptionMenu_ProcessInput())
        {
        case 1:
            sOptionMenuPtr->loadState++;
            break;
        case 2:
            LoadBgTiles(1, GetUserWindowGraphics(sOptionMenuPtr->option[MENUITEM_FRAMETYPE])->tiles, 0x120, 0x1AA);
            LoadPalette(GetUserWindowGraphics(sOptionMenuPtr->option[MENUITEM_FRAMETYPE])->palette, BG_PLTT_ID(2), PLTT_SIZE_4BPP);
            BufferOptionMenuString(sOptionMenuPtr->cursorPos);
            break;
        case 3:
            UpdateSettingSelectionDisplay(sOptionMenuPtr->cursorPos);
            break;
        case 4:
            BufferOptionMenuString(sOptionMenuPtr->cursorPos);
            break;
        }
        break;
    case 3:
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 0x10, RGB_BLACK);
        sOptionMenuPtr->loadState++;
        break;
    case 4:
        if (gPaletteFade.active)
            return;
        sOptionMenuPtr->loadState++;
        break;
    case 5:
        CloseAndSaveOptionMenu(taskId);
        break;
    }
}

