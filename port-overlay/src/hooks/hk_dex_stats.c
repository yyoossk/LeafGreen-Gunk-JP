#include "global.h"
#include "gflib.h"
#include "list_menu.h"
#include "pokedex.h"
#include "item.h"
#include "menu.h"
#include "string_util.h"
#include "sound.h"
#include "constants/songs.h"
#include "constants/pokemon.h"
// 赤フルカラー: ずかんの せつめいの ページで SELECT -> 種族値と しんかの しかた (もう一度 SELECT で せつめいに もどる)

struct PokedexScreenData
{
    u8 taskId;
    u8 state;
    u8 data[2];
    u8 areaMarkersTaskId;
    u32 unlockedCategories;
    u32 modeSelectInput;
    u16 modeSelectItemsAbove;
    u16 modeSelectCursorPos;
    u8 modeSelectWindowId;
    u8 selectionIconWindowId;
    u8 dexCountsWindowId;
    u8 modeSelectListMenuId;
    u16 pageSpecies[4];
    u8 categoryMonWindowIds[4];
    u8 categoryMonInfoWindowIds[4];
    u8 category;
    u8 firstPageInCategory;
    u8 lastPageInCategory;
    u8 pageNum;
    u8 numMonsOnPage;
    u8 categoryCursorPosInPage;
    u8 categoryPageSelectionCursorTimer;
    u8 parentOfCategoryMenu;
    u32 characteristicMenuInput;
    u16 kantoOrderMenuItemsAbove;
    u16 kantoOrderMenuCursorPos;
    u16 characteristicOrderMenuItemsAbove;
    u16 characteristicOrderMenuCursorPos;
    u16 nationalOrderMenuItemsAbove;
    u16 nationalOrderMenuCursorPos;
    u8 numericalOrderWindowId;
    u8 orderedListMenuTaskId;
    u8 dexOrderId;
    struct ListMenuItem * listItems;
    u16 orderedDexCount;
    u8 windowIds[0x10];
    u16 dexSpecies;
};

#define sJpDex (*(struct PokedexScreenData **)0x0203AC68)
#define JpBaseStats   ((const u8 *)0x0820C980)     // 28 bytes per species: hp atk def spe spa spd
#define JpSpeciesNames ((const u8 (*)[6])0x081FF4AC)
#define JpEvolutions  ((const u16 *)0x08211954)    // 5 x {method, param, target, pad} per species
#define JpDexPrintFlavorText ((void (*)(u8, u16, u8, u8))0x08106831)

extern const u8 gJpText_DexStats1[];
extern const u8 gJpText_DexStats2[];
extern const u8 gJpText_DexStats3[];
extern const u8 gJpText_DexEvoNone[];
extern const u8 gJpText_DexEvoLv[];
extern const u8 gJpText_DexEvoTrade[];
extern const u8 gJpText_DexEvoFriend[];
extern const u8 gJpText_DexEvoSep[];
extern const u8 gJpText_DexEvoMore[];

__attribute__((section("ewram_late"))) static u8 sJpDexStatsShown = 0;
__attribute__((section("ewram_late"))) static u16 sJpDexStatsSpecies = 0;

static u8 EvoCategory(u16 method)
{
    switch (method)
    {
    case EVO_FRIENDSHIP:
    case EVO_FRIENDSHIP_DAY:
    case EVO_FRIENDSHIP_NIGHT:
        return 1;
    case EVO_TRADE:
    case EVO_TRADE_ITEM:
        return 2;
    case EVO_ITEM:
        return 3;
    case 0xFFFF:
        return 0;
    default:
        return 4;
    }
}

static u8 *AppendEvoToken(u8 *p, u16 method, u16 param)
{
    switch (method)
    {
    case EVO_FRIENDSHIP:
    case EVO_FRIENDSHIP_DAY:
    case EVO_FRIENDSHIP_NIGHT:
        return StringCopy(p, gJpText_DexEvoFriend);
    case EVO_TRADE:
    case EVO_TRADE_ITEM:
        return StringCopy(p, gJpText_DexEvoTrade);
    case EVO_ITEM:
        return StringCopy(p, ItemId_GetName(param));
    default:
        p = StringCopy(p, gJpText_DexEvoLv);
        return ConvertIntToDecimalStringN(p, param, STR_CONV_MODE_LEFT_ALIGN, 3);
    }
}

static void PrintJpDexStats(u8 windowId, u16 species)
{
    const u8 *bs = JpBaseStats + species * 28;
    const u16 *evo = JpEvolutions + species * 20;
    u8 *p;
    u8 i, n = 0;
    u16 lastMethod = 0xFFFF, lastParam = 0xFFFF;

    ConvertIntToDecimalStringN(gStringVar1, bs[0], STR_CONV_MODE_LEFT_ALIGN, 3);
    ConvertIntToDecimalStringN(gStringVar2, bs[1], STR_CONV_MODE_LEFT_ALIGN, 3);
    ConvertIntToDecimalStringN(gStringVar3, bs[2], STR_CONV_MODE_LEFT_ALIGN, 3);
    p = StringExpandPlaceholders(gStringVar4, gJpText_DexStats1);
    *p++ = CHAR_NEWLINE;
    ConvertIntToDecimalStringN(gStringVar1, bs[4], STR_CONV_MODE_LEFT_ALIGN, 3);
    ConvertIntToDecimalStringN(gStringVar2, bs[5], STR_CONV_MODE_LEFT_ALIGN, 3);
    ConvertIntToDecimalStringN(gStringVar3, bs[3], STR_CONV_MODE_LEFT_ALIGN, 3);
    p = StringExpandPlaceholders(p, gJpText_DexStats2);
    *p++ = CHAR_NEWLINE;
    ConvertIntToDecimalStringN(gStringVar1, bs[0] + bs[1] + bs[2] + bs[3] + bs[4] + bs[5], STR_CONV_MODE_LEFT_ALIGN, 3);
    p = StringExpandPlaceholders(p, gJpText_DexStats3);
    for (i = 0; i < 5; i++)
    {
        u16 method = evo[i * 4], param = evo[i * 4 + 1];
        if (method == 0)
            break;
        if (EvoCategory(method) == EvoCategory(lastMethod)
         && (EvoCategory(method) <= 2 || param == lastParam))
            continue;
        if (n == 1 && evo[2 * 4] != 0)  // 3 ways or more (イーブイ): first one + など
        {
            p = StringCopy(p, gJpText_DexEvoMore);
            break;
        }
        if (n == 2)
            break;
        if (n != 0)
            p = StringCopy(p, gJpText_DexEvoSep);
        p = AppendEvoToken(p, method, param);
        lastMethod = method;
        lastParam = param;
        n++;
    }
    if (n == 0)
        p = StringCopy(p, gJpText_DexEvoNone);
    FillWindowPixelBuffer(windowId, PIXEL_FILL(0));
    {
        static const u8 color[3] = {0, 1, 2};
        AddTextPrinterParameterized3(windowId, FONT_SMALL, 8, 8, color, TEXT_SKIP_DRAW, gStringVar4);
    }
    PutWindowTilemap(windowId);
    CopyWindowToVram(windowId, COPYWIN_GFX);
}

// Task_DexScreen_ShowMonPage state 5 (before START = cry)
void JpDexMonPageInput(void)
{
    struct PokedexScreenData *d = sJpDex;
    u8 win;

    if (d == NULL || d->state != 5)
        return;
    win = d->windowIds[2];
    if (sJpDexStatsSpecies != d->dexSpecies)
    {
        sJpDexStatsShown = 0;
        sJpDexStatsSpecies = d->dexSpecies;
    }
    if (!JOY_NEW(SELECT_BUTTON) || win == 0xFF)
        return;
    if (!GetSetPokedexFlag(SpeciesToNationalPokedexNum(d->dexSpecies), FLAG_GET_CAUGHT))
        return;
    PlaySE(SE_SELECT);
    sJpDexStatsShown ^= 1;
    if (sJpDexStatsShown)
        PrintJpDexStats(win, d->dexSpecies);
    else
    {
        FillWindowPixelBuffer(win, PIXEL_FILL(0));
        JpDexPrintFlavorText(win, d->dexSpecies, 0, 8);
        PutWindowTilemap(win);
        CopyWindowToVram(win, COPYWIN_GFX);
    }
}
