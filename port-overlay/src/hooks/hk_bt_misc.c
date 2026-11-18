#include "global.h"
#include "event_data.h"
#include "pokemon.h"
#include "string_util.h"
#include "window.h"
#include "text.h"
#include "constants/region_map_sections.h"
// FRLG+ RS Battle Tower, the JP-side helpers: the tower's map name, the records board, the outside tileset's
// animation (flags / flowers), RecalculatePartyStats.

#define JP_FONT_NORMAL 2
#define JP_KANTO_MAPSEC_START 0x58
#define JP_MAPSEC_NONE 0xC5
u8 JpCreateWindowFromRect(u8 x, u8 y, u8 w, u8 h);
void JpSetStdWindowBorderStyle(u8 windowId, bool8 copyToVram);
void JpScheduleBgCopyTilemapToVram(u8 bg);
void ClearStdWindowAndFrameToTransparent(u8 windowId, bool8 copyToVram);
u16 JpAddTextPrinterParameterized(u8 windowId, u8 fontId, const u8 *str, u8 x, u8 y, u8 speed, void *callback);
bool8 IsCeladonDeptStoreMapsec(u16 mapsec);
extern const u8 *const gJpMapNames[];          // JP sMapNames (0x083B400C)
extern const u8 gJpMapsecName_CeladonDept[];   // JP sMapsecName_CELADON_DEPT_ (0x083B1593)

// ---------------------------------------------------------------- map name: MAPSEC_BATTLE_FRONTIER is the Battle Tower
static const u8 sText_BattleTower[] = _("バトルタワー");

u8 *GetMapName(u8 *dst0, u16 mapsec, u16 fill)
{
    u8 *dst;
    u16 i;
    u16 idx;

    if (mapsec == MAPSEC_BATTLE_FRONTIER)
        dst = StringCopy(dst0, sText_BattleTower);
    else if ((idx = mapsec - JP_KANTO_MAPSEC_START) < JP_MAPSEC_NONE - JP_KANTO_MAPSEC_START)
    {
        if (IsCeladonDeptStoreMapsec(mapsec) == TRUE)
            dst = StringCopy(dst0, gJpMapsecName_CeladonDept);
        else
            dst = StringCopy(dst0, gJpMapNames[idx]);
    }
    else
    {
        if (fill == 0)
            fill = 18;
        return StringFill(dst0, CHAR_SPACE, fill);
    }
    if (fill != 0)
    {
        for (i = dst - dst0; i < fill; i++)
            *dst++ = CHAR_SPACE;
        *dst = EOS;
    }
    return dst;
}

// ---------------------------------------------------------------- tileset animation (FRLG+ InitTilesetAnim_BattleFrontierOutsideEast)
#define sSecondaryTilesetAnimCounter    (*(u16 *)0x03000FB2)
#define sSecondaryTilesetAnimCounterMax (*(u16 *)0x03000FB4)
#define sSecondaryTilesetAnimCallback   (*(void (**)(u16))0x03000FBC)
void AppendTilesetAnimToBuffer(const u16 *src, u16 *dest, u16 size);
extern const u8 gJpBFEAnimFlag[];
extern const u8 gJpBFEAnimFlower[];

static void TilesetAnim_JpBattleFrontierOutsideEast(u16 timer)
{
    if (timer % 16 == 0)
        AppendTilesetAnimToBuffer((const u16 *)(gJpBFEAnimFlower + ((timer >> 4) % 4) * 0x80), (u16 *)(BG_VRAM + TILE_OFFSET_4BPP(0x312)), 0x80);
    if (timer % 8 == 0)
        AppendTilesetAnimToBuffer((const u16 *)(gJpBFEAnimFlag + ((timer >> 3) % 4) * 0xC0), (u16 *)(BG_VRAM + TILE_OFFSET_4BPP(0x300)), 0xC0);
}

void InitTilesetAnim_JpBattleFrontierOutsideEast(void)
{
    sSecondaryTilesetAnimCounter = 0;
    sSecondaryTilesetAnimCounterMax = 256;
    sSecondaryTilesetAnimCallback = TilesetAnim_JpBattleFrontierOutsideEast;
}

// ---------------------------------------------------------------- party
void RecalculatePartyStats(void)
{
    u32 i;
    for (i = 0; i < gPlayerPartyCount; i++)
        CalculateMonStats(&gPlayerParty[i]);
}

// ---------------------------------------------------------------- records board in the lobby (FRLG+ ShowBattleTowerRecords)
static EWRAM_DATA u8 sRecordsWindowId = 0;
static const u8 sText_Title[] = _("バトルタワー せいせき");
static const u8 sText_Lv50[] = _("レベル50");
static const u8 sText_Open[] = _("オープンレベル");
static const u8 sText_Current[] = _("げんざい");
static const u8 sText_Prev[] = _("まえかい");
static const u8 sText_Record[] = _("さいこう");
static const u8 sText_Wins[] = _("れんしょう");

static bool8 IsStreakCurrent(u8 level)
{
    switch (gSaveBlock2Ptr->battleTower.var_4AE[level])
    {
    case 2:
    case 3:
    case 6:
        return TRUE;
    default:
        return FALSE;
    }
}

static void PrintStreak(const u8 *label, u16 num, u8 y)
{
    u8 buf[16];
    u8 *p;

    if (num > 9999)
        num = 9999;
    JpAddTextPrinterParameterized(sRecordsWindowId, JP_FONT_NORMAL, label, 24, y, TEXT_SKIP_DRAW, NULL);
    p = ConvertIntToDecimalStringN(buf, num, STR_CONV_MODE_RIGHT_ALIGN, 4);
    StringCopy(p, sText_Wins);
    JpAddTextPrinterParameterized(sRecordsWindowId, JP_FONT_NORMAL, buf, 96, y, TEXT_SKIP_DRAW, NULL);
}

void JpBT_ShowRecords(void)
{
    u8 level;

    sRecordsWindowId = JpCreateWindowFromRect(2, 1, 24, 14);
    JpSetStdWindowBorderStyle(sRecordsWindowId, FALSE);
    FillWindowPixelBuffer(sRecordsWindowId, PIXEL_FILL(1));
    JpAddTextPrinterParameterized(sRecordsWindowId, JP_FONT_NORMAL, sText_Title, 48, 0, TEXT_SKIP_DRAW, NULL);
    for (level = 0; level < 2; level++)
    {
        u8 y = 16 + level * 48;
        JpAddTextPrinterParameterized(sRecordsWindowId, JP_FONT_NORMAL, level ? sText_Open : sText_Lv50, 0, y, TEXT_SKIP_DRAW, NULL);
        PrintStreak(IsStreakCurrent(level) ? sText_Current : sText_Prev, gSaveBlock2Ptr->battleTower.currentWinStreaks[level], y + 16);
        PrintStreak(sText_Record, gSaveBlock2Ptr->battleTower.recordWinStreaks[level], y + 32);
    }
    PutWindowTilemap(sRecordsWindowId);
    CopyWindowToVram(sRecordsWindowId, COPYWIN_FULL);
    JpScheduleBgCopyTilemapToVram(0);
}

void JpBT_RemoveRecords(void)
{
    ClearStdWindowAndFrameToTransparent(sRecordsWindowId, TRUE);
    RemoveWindow(sRecordsWindowId);
    JpScheduleBgCopyTilemapToVram(0);
}
