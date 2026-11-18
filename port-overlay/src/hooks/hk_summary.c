#include "global.h"
#include "gflib.h"
#include "pokemon.h"
#include "string_util.h"
#include "constants/songs.h"
// Gunk's IV/EV view on the SKILLS page, written against the Japanese summary screen's layout
EWRAM_DATA u8 gJpGunkStatView = 0;

#define JP_SUMMARY   (*(u8 **)0x0203B0B4)
#define JP_XPOS      (*(u16 **)0x0203B0B8)
void JpBufferMonSkills(void);
void JpPokeSum_PrintRightPaneText(void);

static const u8 sJpIVHeader[] = _("こたいち");
static const u8 sJpEVHeader[] = _("どりょくち");
void JpPokeSum_PrintPageHeader(const u8 *str);
#define JP_SKILLS_HEADER (*(const u8 **)0x0813848C)

void JpSum_IvEv(void)
{
    static const u8 sIVData[NUM_STATS] = {MON_DATA_HP_IV, MON_DATA_ATK_IV, MON_DATA_DEF_IV, MON_DATA_SPATK_IV, MON_DATA_SPDEF_IV, MON_DATA_SPEED_IV};
    static const u8 sEVData[NUM_STATS] = {MON_DATA_HP_EV, MON_DATA_ATK_EV, MON_DATA_DEF_EV, MON_DATA_SPATK_EV, MON_DATA_SPDEF_EV, MON_DATA_SPEED_EV};
    static const u16 sBufOffsets[5] = {0x308C, 0x3091, 0x3096, 0x309B, 0x30A0}; // atk, def, sp.atk, sp.def, speed
    u8 *s = JP_SUMMARY;
    u16 *x = JP_XPOS;
    struct Pokemon *mon = (struct Pokemon *)(s + 0x323C);
    const u8 *data;
    u8 tempStr[8];
    u8 *buf;
    int i;

    if (gJpGunkStatView == 0)
        return;
    data = gJpGunkStatView == 1 ? sIVData : sEVData;
    buf = s + 0x3080;
    ConvertIntToDecimalStringN(buf, GetMonData(mon, data[0]), STR_CONV_MODE_LEFT_ALIGN, 3);
    x[1] = 63 - StringLength(buf) * 9;
    for (i = 0; i < 5; i++)
    {
        buf = s + sBufOffsets[i];
        ConvertIntToDecimalStringN(buf, GetMonData(mon, data[i + 1]), STR_CONV_MODE_LEFT_ALIGN, 3);
        x[2 + i] = 27 - StringLength(buf) * 9;
    }
}

// A on the SKILLS page: stats -> IVs -> EVs (not for an Egg, nor the trade partner's Pokémon)
void JpSum_CycleView(void)
{
    u8 *s = JP_SUMMARY;

    if (GetMonData((struct Pokemon *)(s + 0x323C), MON_DATA_IS_EGG))
        return;
    if (*(u32 *)(s + 0x32A4) == 0x0804C67D && *(u32 *)(s + 0x3024) == 1)
        return;
    PlaySE(SE_SELECT);
    gJpGunkStatView = (gJpGunkStatView + 1) % 3;
    JpBufferMonSkills();
    JpPokeSum_PrintRightPaneText();
    CopyWindowToVram(s[0x3003], 2);
    JpPokeSum_PrintPageHeader(gJpGunkStatView == 0 ? JP_SKILLS_HEADER : gJpGunkStatView == 1 ? sJpIVHeader : sJpEVHeader);
}

// FRLG+: the stat a nature raises is printed in red, the one it lowers in blue (normal view only)
void JpAddTextPrinterParameterized3(u8 windowId, u8 fontId, u8 x, u8 y, const u8 *color, s8 speed, const u8 *str);
static const u8 sJpColorsRed[3] = {0, 1, 10};
static const u8 sJpColorsBlue[3] = {0, 7, 10};
#define JP_COLORS_RED  sJpColorsRed
#define JP_COLORS_BLUE sJpColorsBlue
static void PrintStatNat(u8 idx, u8 windowId, u8 fontId, u8 x, u8 y, const u8 *color, s8 speed, const u8 *str)
{
    static const u8 sNatureStat[5] = {0, 1, 3, 4, 2}; // atk, def, sp.atk, sp.def, speed -> nature stat order
    if (gJpGunkStatView == 0)
    {
        u32 pid = *(u32 *)(JP_SUMMARY + 0x323C);
        u8 nature = pid % 25;
        u8 up = nature / 5, down = nature % 5;
        if (up != down)
        {
            if (sNatureStat[idx] == up)
                color = JP_COLORS_RED;
            else if (sNatureStat[idx] == down)
                color = JP_COLORS_BLUE;
        }
    }
    JpAddTextPrinterParameterized3(windowId, fontId, x, y, color, speed, str);
}
void JpSum_PrintStat0(u8 w, u8 f, u8 x, u8 y, const u8 *c, s8 s, const u8 *str) { PrintStatNat(0, w, f, x, y, c, s, str); }
void JpSum_PrintStat1(u8 w, u8 f, u8 x, u8 y, const u8 *c, s8 s, const u8 *str) { PrintStatNat(1, w, f, x, y, c, s, str); }
void JpSum_PrintStat2(u8 w, u8 f, u8 x, u8 y, const u8 *c, s8 s, const u8 *str) { PrintStatNat(2, w, f, x, y, c, s, str); }
void JpSum_PrintStat3(u8 w, u8 f, u8 x, u8 y, const u8 *c, s8 s, const u8 *str) { PrintStatNat(3, w, f, x, y, c, s, str); }
void JpSum_PrintStat4(u8 w, u8 f, u8 x, u8 y, const u8 *c, s8 s, const u8 *str) { PrintStatNat(4, w, f, x, y, c, s, str); }
