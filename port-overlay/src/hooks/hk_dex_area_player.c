#include "global.h"
#include "gflib.h"
#include "decompress.h"
#include "field_specials.h"
#include "overworld.h"
#include "pokedex.h"
#include "pokedex_area_markers.h"
#include "constants/region_map_sections.h"

// ずかんの「ぶんぷ」に、いま 主人公が いる ばしょを タウンマップの 主人公の アイコンで だす（点滅）。
// JP DexScreen_DrawMonAreaPage の CreatePokedexAreaMarkers よびだし (0x08107238) と、
// DexScreen_DestroyAreaScreenResources の DestroyPokedexAreaMarkers よびだし (0x081072FC) を つなぎかえる。

#define JpAreaMarkers      ((const s8 (*)[4])0x08421194)   // sAreaMarkers: {shape, x, y, 0}
#define JpPlayerIcon_Red    ((const u32 *)0x083B1884)
#define JpPlayerIcon_RedPal ((const u16 *)0x083B15DC)
#define JpPlayerIcon_Leaf   ((const u32 *)0x083B18FC)
#define JpPlayerIcon_LeafPal ((const u16 *)0x083B15FC)

#define TAG_JP_DEX_PLAYER 0x5AA1
#define PAL_JP_DEX_PLAYER 14

static const u16 sDexAreas_Kanto[][2] = {
    { MAPSEC_PALLET_TOWN,         DEX_AREA_PALLET_TOWN },
    { MAPSEC_VIRIDIAN_CITY,       DEX_AREA_VIRIDIAN_CITY },
    { MAPSEC_PEWTER_CITY,         DEX_AREA_PEWTER_CITY },
    { MAPSEC_CERULEAN_CITY,       DEX_AREA_CERULEAN_CITY },
    { MAPSEC_LAVENDER_TOWN,       DEX_AREA_LAVENDER_TOWN },
    { MAPSEC_VERMILION_CITY,      DEX_AREA_VERMILION_CITY },
    { MAPSEC_CELADON_CITY,        DEX_AREA_CELADON_CITY },
    { MAPSEC_FUCHSIA_CITY,        DEX_AREA_FUCHSIA_CITY },
    { MAPSEC_CINNABAR_ISLAND,     DEX_AREA_CINNABAR_ISLAND },
    { MAPSEC_INDIGO_PLATEAU,      DEX_AREA_INDIGO_PLATEAU },
    { MAPSEC_SAFFRON_CITY,        DEX_AREA_SAFFRON_CITY },
    { MAPSEC_ROUTE_4_POKECENTER,  DEX_AREA_ROUTE_4 },
    { MAPSEC_ROUTE_10_POKECENTER, DEX_AREA_ROUTE_10 },
    { MAPSEC_ROUTE_1,             DEX_AREA_ROUTE_1 },
    { MAPSEC_ROUTE_2,             DEX_AREA_ROUTE_2 },
    { MAPSEC_ROUTE_3,             DEX_AREA_ROUTE_3 },
    { MAPSEC_ROUTE_4,             DEX_AREA_ROUTE_4 },
    { MAPSEC_ROUTE_5,             DEX_AREA_ROUTE_5 },
    { MAPSEC_ROUTE_6,             DEX_AREA_ROUTE_6 },
    { MAPSEC_ROUTE_7,             DEX_AREA_ROUTE_7 },
    { MAPSEC_ROUTE_8,             DEX_AREA_ROUTE_8 },
    { MAPSEC_ROUTE_9,             DEX_AREA_ROUTE_9 },
    { MAPSEC_ROUTE_10,            DEX_AREA_ROUTE_10 },
    { MAPSEC_ROUTE_11,            DEX_AREA_ROUTE_11 },
    { MAPSEC_ROUTE_12,            DEX_AREA_ROUTE_12 },
    { MAPSEC_ROUTE_13,            DEX_AREA_ROUTE_13 },
    { MAPSEC_ROUTE_14,            DEX_AREA_ROUTE_14 },
    { MAPSEC_ROUTE_15,            DEX_AREA_ROUTE_15 },
    { MAPSEC_ROUTE_16,            DEX_AREA_ROUTE_16 },
    { MAPSEC_ROUTE_17,            DEX_AREA_ROUTE_17 },
    { MAPSEC_ROUTE_18,            DEX_AREA_ROUTE_18 },
    { MAPSEC_ROUTE_19,            DEX_AREA_ROUTE_19 },
    { MAPSEC_ROUTE_20,            DEX_AREA_ROUTE_20 },
    { MAPSEC_ROUTE_21,            DEX_AREA_ROUTE_21 },
    { MAPSEC_ROUTE_22,            DEX_AREA_ROUTE_22 },
    { MAPSEC_ROUTE_23,            DEX_AREA_ROUTE_23 },
    { MAPSEC_ROUTE_24,            DEX_AREA_ROUTE_24 },
    { MAPSEC_ROUTE_25,            DEX_AREA_ROUTE_25 },
    { MAPSEC_VIRIDIAN_FOREST,     DEX_AREA_VIRIDIAN_FOREST },
    { MAPSEC_MT_MOON,             DEX_AREA_MT_MOON },
    { MAPSEC_S_S_ANNE,            DEX_AREA_VERMILION_CITY },
    { MAPSEC_UNDERGROUND_PATH,    DEX_AREA_SAFFRON_CITY },
    { MAPSEC_UNDERGROUND_PATH_2,  DEX_AREA_SAFFRON_CITY },
    { MAPSEC_DIGLETTS_CAVE,       DEX_AREA_DIGLETTS_CAVE },
    { MAPSEC_KANTO_VICTORY_ROAD,  DEX_AREA_VICTORY_ROAD },
    { MAPSEC_ROCKET_HIDEOUT,      DEX_AREA_CELADON_CITY },
    { MAPSEC_SILPH_CO,            DEX_AREA_SAFFRON_CITY },
    { MAPSEC_POKEMON_MANSION,     DEX_AREA_POKEMON_MANSION },
    { MAPSEC_KANTO_SAFARI_ZONE,   DEX_AREA_SAFARI_ZONE },
    { MAPSEC_POKEMON_LEAGUE,      DEX_AREA_VICTORY_ROAD },
    { MAPSEC_ROCK_TUNNEL,         DEX_AREA_ROCK_TUNNEL },
    { MAPSEC_SEAFOAM_ISLANDS,     DEX_AREA_SEAFOAM_ISLANDS },
    { MAPSEC_POKEMON_TOWER,       DEX_AREA_POKEMON_TOWER },
    { MAPSEC_CERULEAN_CAVE,       DEX_AREA_CERULEAN_CAVE },
    { MAPSEC_POWER_PLANT,         DEX_AREA_POWER_PLANT }
};

static const u16 sDexAreas_Sevii1[][2] = {
	{ MAPSEC_KINDLE_ROAD,    DEX_AREA_KINDLE_ROAD },
	{ MAPSEC_TREASURE_BEACH, DEX_AREA_TREASURE_BEACH },
	{ MAPSEC_ONE_ISLAND,     DEX_AREA_ONE_ISLAND },
	{ MAPSEC_MT_EMBER,       DEX_AREA_MT_EMBER }    
};

static const u16 sDexAreas_Sevii2[][2] = {
	{ MAPSEC_CAPE_BRINK, DEX_AREA_CAPE_BRINK },
	{ MAPSEC_TWO_ISLAND, DEX_AREA_TWO_ISLAND }    
};

static const u16 sDexAreas_Sevii3[][2] = {
	{ MAPSEC_BOND_BRIDGE,     DEX_AREA_BOND_BRIDGE },
	{ MAPSEC_THREE_ISLE_PORT, DEX_AREA_THREE_ISLE_PATH },
	{ MAPSEC_THREE_ISLAND,    DEX_AREA_THREE_ISLAND },
	{ MAPSEC_BERRY_FOREST,    DEX_AREA_BERRY_FOREST },
	{ MAPSEC_THREE_ISLE_PATH, DEX_AREA_THREE_ISLE_PATH }    
};

static const u16 sDexAreas_Sevii4[][2] = {
	{ MAPSEC_FOUR_ISLAND,  DEX_AREA_FOUR_ISLAND },
	{ MAPSEC_ICEFALL_CAVE, DEX_AREA_ICEFALL_CAVE }    
};

static const u16 sDexAreas_Sevii5[][2] = {
	{ MAPSEC_RESORT_GORGEOUS,  DEX_AREA_RESORT_GORGEOUS },
	{ MAPSEC_WATER_LABYRINTH,  DEX_AREA_WATER_LABYRINTH },
	{ MAPSEC_FIVE_ISLE_MEADOW, DEX_AREA_FIVE_ISLE_MEADOW },
	{ MAPSEC_MEMORIAL_PILLAR,  DEX_AREA_MEMORIAL_PILLAR },
	{ MAPSEC_FIVE_ISLAND,      DEX_AREA_FIVE_ISLAND },
	{ MAPSEC_ROCKET_WAREHOUSE, DEX_AREA_FIVE_ISLE_MEADOW },
	{ MAPSEC_LOST_CAVE,        DEX_AREA_LOST_CAVE }    
};

static const u16 sDexAreas_Sevii6[][2] = {
	{ MAPSEC_OUTCAST_ISLAND, DEX_AREA_OUTCAST_ISLAND },
	{ MAPSEC_GREEN_PATH,     DEX_AREA_GREEN_PATH },
	{ MAPSEC_WATER_PATH,     DEX_AREA_WATER_PATH },
	{ MAPSEC_RUIN_VALLEY,    DEX_AREA_RUIN_VALLEY },
	{ MAPSEC_DOTTED_HOLE,    DEX_AREA_DOTTED_HOLE },
	{ MAPSEC_PATTERN_BUSH,   DEX_AREA_PATTERN_BUSH },
	{ MAPSEC_ALTERING_CAVE,  DEX_AREA_ALTERING_CAVE }    
};

static const u16 sDexAreas_Sevii7[][2] = {
	{ MAPSEC_TRAINER_TOWER,   DEX_AREA_TRAINER_TOWER },
	{ MAPSEC_CANYON_ENTRANCE, DEX_AREA_CANYON_ENTRANCE },
	{ MAPSEC_SEVAULT_CANYON,  DEX_AREA_SEVAULT_CANYON },
	{ MAPSEC_TANOBY_RUINS,    DEX_AREA_TANOBY_RUINS },
	{ MAPSEC_MONEAN_CHAMBER,  DEX_AREA_TANOBY_CHAMBER },
	{ MAPSEC_LIPTOO_CHAMBER,  DEX_AREA_TANOBY_CHAMBER },
	{ MAPSEC_WEEPTH_CHAMBER,  DEX_AREA_TANOBY_CHAMBER },
	{ MAPSEC_DILFORD_CHAMBER, DEX_AREA_TANOBY_CHAMBER },
	{ MAPSEC_SCUFIB_CHAMBER,  DEX_AREA_TANOBY_CHAMBER },
	{ MAPSEC_RIXY_CHAMBER,    DEX_AREA_TANOBY_CHAMBER },
	{ MAPSEC_VIAPOIS_CHAMBER, DEX_AREA_TANOBY_CHAMBER }    
};

static const struct
{
    const u16 (*table)[2];
    s32 count;
} sSeviiDexAreas[] = {
    { sDexAreas_Sevii1, ARRAY_COUNT(sDexAreas_Sevii1) },
    { sDexAreas_Sevii2, ARRAY_COUNT(sDexAreas_Sevii2) },
    { sDexAreas_Sevii3, ARRAY_COUNT(sDexAreas_Sevii3) },
    { sDexAreas_Sevii4, ARRAY_COUNT(sDexAreas_Sevii4) },
    { sDexAreas_Sevii5, ARRAY_COUNT(sDexAreas_Sevii5) },
    { sDexAreas_Sevii6, ARRAY_COUNT(sDexAreas_Sevii6) },
    { sDexAreas_Sevii7, ARRAY_COUNT(sDexAreas_Sevii7) }
};


static const u8 sMarkerSize[][2] = { {8, 8}, {16, 8}, {8, 16}, {32, 16}, {16, 32}, {32, 16}, {16, 32} };

static EWRAM_DATA u8 sJpDexPlayerSpriteId = 0;   // id + 1

static u16 FindDexArea(u16 mapSec)
{
    u32 i, j;
    u8 sevii;

    for (i = 0; i < ARRAY_COUNT(sDexAreas_Kanto); i++)
        if (sDexAreas_Kanto[i][0] == mapSec)
            return sDexAreas_Kanto[i][1];
    sevii = GetUnlockedSeviiAreas();
    for (j = 0; j < ARRAY_COUNT(sSeviiDexAreas); j++)
    {
        if (!((sevii >> j) & 1))
            continue;
        for (i = 0; i < sSeviiDexAreas[j].count; i++)
            if (sSeviiDexAreas[j].table[i][0] == mapSec)
                return sSeviiDexAreas[j].table[i][1];
    }
    return DEX_AREA_NONE;
}

static u16 GetPlayerDexArea(void)
{
    u16 area = FindDexArea(gMapHeader.regionMapSectionId);
    if (area == DEX_AREA_NONE)
    {
        // たてものの なかなど: あなをほる・あなぬけのヒモで でる ばしょ
        struct WarpData *w = &gSaveBlock1Ptr->escapeWarp;
        if (w->mapGroup != -1 || w->mapNum != -1)
            area = FindDexArea(Overworld_GetMapHeaderByGroupAndId(w->mapGroup, w->mapNum)->regionMapSectionId);
    }
    return area;
}

static void SpriteCB_JpDexPlayer(struct Sprite *sprite)
{
    if (++sprite->data[0] >= 48)
        sprite->data[0] = 0;
    sprite->invisible = (sprite->data[0] >= 32);
}

static const struct OamData sOam_JpDexPlayer = {
    .shape = SPRITE_SHAPE(16x16),
    .size = SPRITE_SIZE(16x16),
    .priority = 0,
};

u8 JpCreatePokedexAreaMarkers(u16 species, u16 tilesTag, u8 palIdx, u8 y)
{
    u8 taskId = CreatePokedexAreaMarkers(species, tilesTag, palIdx, y);
    u16 area = GetPlayerDexArea();
    struct CompressedSpriteSheet sheet;
    struct SpriteTemplate tmpl;
    const s8 *m;
    u8 spriteId;
    s16 x, py;

    sJpDexPlayerSpriteId = 0;
    if (area == DEX_AREA_NONE)
        return taskId;
    m = JpAreaMarkers[area];
    x = 104 - 4 + m[1] + sMarkerSize[(u8)m[0]][0] / 2;
    py = y + 32 - 4 + m[2] + sMarkerSize[(u8)m[0]][1] / 2;

    sheet.data = gSaveBlock2Ptr->playerGender == FEMALE ? JpPlayerIcon_Leaf : JpPlayerIcon_Red;
    sheet.size = 0x80;
    sheet.tag = TAG_JP_DEX_PLAYER;
    LoadCompressedSpriteSheet(&sheet);
    LoadPalette(gSaveBlock2Ptr->playerGender == FEMALE ? JpPlayerIcon_LeafPal : JpPlayerIcon_RedPal, OBJ_PLTT_ID(PAL_JP_DEX_PLAYER), PLTT_SIZE_4BPP);
    tmpl = gDummySpriteTemplate;
    tmpl.tileTag = TAG_JP_DEX_PLAYER;
    tmpl.oam = &sOam_JpDexPlayer;
    tmpl.callback = SpriteCB_JpDexPlayer;
    spriteId = CreateSprite(&tmpl, x, py, 0);
    if (spriteId == MAX_SPRITES)
        return taskId;
    gSprites[spriteId].oam.paletteNum = PAL_JP_DEX_PLAYER;
    sJpDexPlayerSpriteId = spriteId + 1;
    // マーカーの なか (OBJ ウインドウ) でも アイコンを みせる
    SetGpuReg(REG_OFFSET_WINOUT, GetGpuReg(REG_OFFSET_WINOUT) | WINOUT_WINOBJ_OBJ);
    return taskId;
}

void JpDestroyPokedexAreaMarkers(u8 taskId)
{
    if (sJpDexPlayerSpriteId != 0)
    {
        DestroySprite(&gSprites[sJpDexPlayerSpriteId - 1]);
        FreeSpriteTilesByTag(TAG_JP_DEX_PLAYER);
        sJpDexPlayerSpriteId = 0;
    }
    DestroyPokedexAreaMarkers(taskId);
}
