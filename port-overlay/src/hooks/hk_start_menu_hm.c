#include "global.h"
#include "gflib.h"
#include "event_data.h"
#include "field_weather.h"
#include "fieldmap.h"
#include "link.h"
#include "overworld.h"
#include "party_menu.h"
#include "pokemon.h"
#include "script.h"
#include "menu.h"
#include "constants/flags.h"
#include "constants/map_types.h"
#include "constants/moves.h"
#include "constants/species.h"

// スタートメニューに「そらをとぶ」「フラッシュ」。
//  そらをとぶ：オレンジバッジ（3つめ）を もっていて、とべる ばしょなら。どうくつ・たてものの なかからも とべる。
//  フラッシュ：グレーバッジ（1つめ）を もっていて、くらい ばしょ（まだ あかるくしていない）なら。
//  ポケモンは その わざを おぼえている ポケモン、いなければ さいしょの タマゴでない ポケモン（ひでんわざは おぼえなくても つかえる）。
// メニューが 8こ いじょうに なると 下の せつめいの まどと かさなるので、そのときは せつめいを ださない（JpStartHelp*）。

#define STARTMENU_JP_HM    10   // 「ひでんわざ」：そらをとぶ・フラッシュを まとめた サブメニュー
#define STARTMENU_JP_HERE  11   // 「このばしょ」：いまいる マップの やせいの ポケモン (hk_dex_here.c)

#define JpAppendToStartMenuItems   ((void (*)(u8))0x0806E501)
#define JpStartMenuExitCallback    ((bool8 (*)(void))0x0806ECA9)
#define JpCleanupOverworldWindows  ((void (*)(void))0x08055C8D)
#define JpCB2_OpenFlyMap           ((void (*)(void))0x080C610D)
#define JpCB2_ReturnToPartyFromFly ((void (*)(void))0x0812533D)
#define JpCB2_ReturnToFieldOpenMenu ((void (*)(void))0x08056145)
#define JpFieldCallback_Flash      ((void (*)(void))0x080CAD71)
#define JpDrawHelpMessageWindowWithText ((void (*)(const u8 *))0x080F89F1)
#define JpPrintTextOnHelpMessageWindow  ((void (*)(const u8 *, u8))0x08113B41)
#define sJpNumStartMenuItems       (*(u8 *)0x02037029)

void DestroySafariZoneStatsWindow(void);

static EWRAM_DATA u8 sJpFlyFromMenu = 0;

bool8 JpCanFlyHere(void)
{
    u8 type = gMapHeader.mapType;
    s8 group = gSaveBlock1Ptr->location.mapGroup, num = gSaveBlock1Ptr->location.mapNum;

    if (Overworld_MapTypeAllowsTeleportAndFly(type) == TRUE)
        return TRUE;
    if (type != MAP_TYPE_UNDERGROUND && type != MAP_TYPE_INDOOR)
        return FALSE;
    if (group == 0)                                       // つうしんの へや
        return FALSE;
    if (group == 2 && num >= 1 && num <= 11 && num != 10) // トレーナータワー（ロビーは よい）
        return FALSE;
    if (group == 42 && num >= 2)                          // バトルタワーの なか
        return FALSE;
    if (InUnionRoom() == TRUE)
        return FALSE;
    return TRUE;
}

// JP SetUpFieldMove_Fly (0x08125318): てもちの メニューから とぶとき
bool8 JpSetUpFieldMove_Fly(void)
{
    sJpFlyFromMenu = FALSE;
    return JpCanFlyHere();
}

// とぶ マップで やめたとき（JP FreeFlyMap の CB2_ReturnToPartyMenuFromFlyMap）
void JpCB2_FlyMapCancel(void)
{
    if (sJpFlyFromMenu)
    {
        sJpFlyFromMenu = FALSE;
        SetMainCallback2(JpCB2_ReturnToFieldOpenMenu);
    }
    else
    {
        SetMainCallback2(JpCB2_ReturnToPartyFromFly);
    }
}

static s8 FindHmMon(u16 move)
{
    s8 i, first = -1;
    for (i = 0; i < PARTY_SIZE; i++)
    {
        u16 species = GetMonData(&gPlayerParty[i], MON_DATA_SPECIES_OR_EGG);
        if (species == SPECIES_NONE || species == SPECIES_EGG)
            continue;
        if (first < 0)
            first = i;
        if (GetMonData(&gPlayerParty[i], MON_DATA_MOVE1) == move || GetMonData(&gPlayerParty[i], MON_DATA_MOVE2) == move
         || GetMonData(&gPlayerParty[i], MON_DATA_MOVE3) == move || GetMonData(&gPlayerParty[i], MON_DATA_MOVE4) == move)
            return i;
    }
    return first;
}

bool8 JpStartMenuShowFly(void)
{
    return FlagGet(FLAG_BADGE03_GET) && FindHmMon(MOVE_FLY) >= 0 && JpCanFlyHere();
}

bool8 JpStartMenuShowFlash(void)
{
    return FlagGet(FLAG_BADGE01_GET) && FindHmMon(MOVE_FLASH) >= 0
        && gMapHeader.cave == TRUE && !FlagGet(FLAG_SYS_FLASH_ACTIVE);
}

void JpAppendStartMenuHms(void)
{
    if (JpStartMenuShowFly() || JpStartMenuShowFlash())
        JpAppendToStartMenuItems(STARTMENU_JP_HM);
    if (FlagGet(FLAG_SYS_POKEDEX_GET))
        JpAppendToStartMenuItems(STARTMENU_JP_HERE);
}

bool8 JpStartMenuFlyCallback(void)
{
    if (gPaletteFade.active)
        return FALSE;
    PlayRainStoppingSoundEffect();
    DestroySafariZoneStatsWindow();
    JpCleanupOverworldWindows();
    gPartyMenu.slotId = FindHmMon(MOVE_FLY);
    sJpFlyFromMenu = TRUE;
    SetMainCallback2(JpCB2_OpenFlyMap);
    return TRUE;
}

bool8 JpStartMenuFlashCallback(void)
{
    JpStartMenuExitCallback();
    LockPlayerFieldControls();
    gPartyMenu.slotId = FindHmMon(MOVE_FLASH);
    JpFieldCallback_Flash();
    return TRUE;
}

// せつめいの まど：メニューが 8こ いじょう（せつめいと かさなる）なら ださない
void JpStartHelpDraw(const u8 *text)
{
    if (sJpNumStartMenuItems <= 7)
        JpDrawHelpMessageWindowWithText(text);
}

void JpStartHelpPrint(const u8 *text, u8 mode)
{
    if (sJpNumStartMenuItems <= 7)
        JpPrintTextOnHelpMessageWindow(text, mode);
}

// ---- 「ひでんわざ」の サブメニュー（スタートメニューの ひだり）
u8 JpCreateWindowFromRect(u8 x, u8 y, u8 w, u8 h);
void JpSetStdWindowBorderStyle(u8 windowId, bool8 copyToVram);
u16 JpAddTextPrinterParameterized(u8 windowId, u8 fontId, const u8 *str, u8 x, u8 y, u8 speed, void *callback);
u8 JpMenu_InitCursor(u8 windowId, u8 fontId, u8 left, u8 top, u8 cursorHeight, u8 numChoices, u8 initialCursorPos);
void JpScheduleBgCopyTilemapToVram(u8 bg);
#define JpMenu_ProcessInput ((s8 (*)(void))0x081104A9)
#define JpClearStdWindowAndFrameToTransparent ((void (*)(u8, bool8))0x0810FF6D)
#define JpShowStartMenu ((void (*)(void))0x0806E9C5)
#define sJpStartMenuCallback (*(void **)0x02037024)
extern const u8 gJpText_MenuFly[];
extern const u8 gJpText_MenuFlash[];

static EWRAM_DATA u8 sJpHmState = 0;
static EWRAM_DATA u8 sJpHmWin = 0;
static EWRAM_DATA u8 sJpHmItems[2] = {0};
static EWRAM_DATA u8 sJpHmCount = 0;

bool8 JpStartMenuHmCallback(void)
{
    s8 r;
    u8 i;

    if (sJpHmState == 0)
    {
        sJpHmCount = 0;
        if (JpStartMenuShowFly())
            sJpHmItems[sJpHmCount++] = 0;
        if (JpStartMenuShowFlash())
            sJpHmItems[sJpHmCount++] = 1;
        sJpHmWin = JpCreateWindowFromRect(9, 0, 8, sJpHmCount * 2);
        JpSetStdWindowBorderStyle(sJpHmWin, FALSE);
        for (i = 0; i < sJpHmCount; i++)
            JpAddTextPrinterParameterized(sJpHmWin, 2, sJpHmItems[i] == 0 ? gJpText_MenuFly : gJpText_MenuFlash, 8, 2 + 16 * i, 0xFF, NULL);
        JpMenu_InitCursor(sJpHmWin, 2, 0, 2, 16, sJpHmCount, 0);
        CopyWindowToVram(sJpHmWin, COPYWIN_FULL);
        JpScheduleBgCopyTilemapToVram(0);
        sJpHmState = 1;
        return FALSE;
    }
    r = JpMenu_ProcessInput();
    if (r == MENU_NOTHING_CHOSEN)
        return FALSE;
    JpClearStdWindowAndFrameToTransparent(sJpHmWin, TRUE);
    ClearWindowTilemap(sJpHmWin);
    RemoveWindow(sJpHmWin);
    JpScheduleBgCopyTilemapToVram(0);
    sJpHmState = 0;
    if (r == MENU_B_PRESSED)
    {
        // スタートメニューに もどる（カーソルの じょうほうは サブメニューで うわがき されたので、メニューを ひらきなおす）
        JpStartMenuExitCallback();
        JpShowStartMenu();
        return TRUE;
    }
    if (sJpHmItems[r] == 0)
    {
        FadeScreen(FADE_TO_BLACK, 0);
        sJpStartMenuCallback = (void *)JpStartMenuFlyCallback;
        return FALSE;
    }
    return JpStartMenuFlashCallback();
}
