#include "global.h"
#include "gflib.h"
#include "battle.h"
#include "battle_interface.h"
#include "battle_anim.h"
#include "menu.h"
#include "string_util.h"
// 赤フルカラー: あいての HP も、こちらの ポケモンと 同じように HPバーの下に 数字で (シングルバトル)
// The opponent's singles healthbox (64x32 main + 64x32 "other") gets its bottom rows (24-31) turned into a
// numbers row in VRAM, and a strip sprite under it redraws the box bottom (border + shadow) one row lower.
// Driven from the opponent healthbar sprite callback (sHealthbarSpriteTemplates[1].callback).

#define JpSpriteCB_HealthBar ((void (*)(struct Sprite *))0x0804761D)
#define TAG_JP_FOE_HP_STRIP 0xD7F0
#define ROW_PLAIN   16   // a plain interior row of the box
#define ROW_NUMBERS 24   // first row turned into the numbers row
#define FOE_HP_NONE 0x7FFF

__attribute__((section("ewram_late"))) static s16 sJpFoeHpShown[MAX_BATTLERS_COUNT];

static void BufSetPix(u8 *buf, u8 x, u8 y, u8 c)
{
    u8 *b = buf + (x >= 64 ? 8 * TILE_SIZE_4BPP : 0) + ((x % 64) / 8) * TILE_SIZE_4BPP + y * 4 + (x % 8) / 2;
    if (x & 1)
        *b = (*b & 0x0F) | (c << 4);
    else
        *b = (*b & 0xF0) | c;
}

void JpFoeHpBarStep(u8 battlerId, s32 value)
{
    struct BattleBarInfo *bar;

    if (GetBattlerSide(battlerId) != B_SIDE_OPPONENT)
        return;
    bar = &gBattleSpritesDataPtr->battleBars[battlerId];
    if (value != -1)
        sJpFoeHpShown[battlerId] = value;
    else
    {
        s32 v = bar->oldValue - bar->receivedValue;
        if (v < 0)
            v = 0;
        if (v > bar->maxValue)
            v = bar->maxValue;
        sJpFoeHpShown[battlerId] = v;
    }
}

static u8 *PixPtr(u16 tileNum, u8 x, u8 y)
{
    u16 t = tileNum + (x >= 64 ? 32 : 0) + (y / 8) * 8 + ((x % 64) / 8);
    return (u8 *)(OBJ_VRAM0 + t * TILE_SIZE_4BPP + (y % 8) * 4 + (x % 8) / 2);
}

static u8 GetPix(u16 tileNum, u8 x, u8 y)
{
    u8 b = *PixPtr(tileNum, x, y);
    return (x & 1) ? (b >> 4) : (b & 0xF);
}

static void SetPix(u16 tileNum, u8 x, u8 y, u8 c)
{
    vu8 *p = PixPtr(tileNum, x, y);
    u16 *p16 = (u16 *)((u32)p & ~1);   // VRAM: 16-bit writes only
    u16 v = *p16;
    u8 shift = ((u32)p & 1) * 8 + (x & 1) * 4;
    v = (v & ~(0xF << shift)) | (c << shift);
    *p16 = v;
}

static const u8 sZeroTiles[64 * TILE_SIZE_4BPP] = {0};
static const struct SpriteSheet sStripSheet = {sZeroTiles, sizeof(sZeroTiles), TAG_JP_FOE_HP_STRIP};
static const struct OamData sStripOam = {.shape = SPRITE_SHAPE(64x32), .size = SPRITE_SIZE(64x32), .priority = 1};
static const struct SpriteTemplate sStripTemplate = {
    .tileTag = TAG_JP_FOE_HP_STRIP, .paletteTag = TAG_HEALTHBOX_PAL, .oam = &sStripOam,
    .anims = gDummySpriteAnimTable, .images = NULL, .affineAnims = gDummySpriteAffineAnimTable, .callback = SpriteCallbackDummy,
};

// strip sprites: data[0] = other half sprite id, data[1] = last HP drawn, data[2] = last max HP drawn
#define sStripOther data[0]
#define sLastHp     data[1]
#define sLastMax    data[2]

// row 16 の x 8-31 は じょうたい いじょうの アイコン（やけど など）の ばしょ。
// アイコンが 出ている ときに その色を 下の行に うつすと 色の かたまりに なるので、ふつうの 中の色を つかう
#define STATUS_X0 8
#define STATUS_X1 32
#define PLAIN_X   36
static u8 PlainPix(u16 hbTile, u8 x)
{
    if (x >= STATUS_X0 && x < STATUS_X1)
        x = PLAIN_X;
    return GetPix(hbTile, x, ROW_PLAIN);
}

static void PatchHealthbox(u16 hbTile, u16 stripTile)
{
    u8 x, y;
    // strip rows 0-7 = the box bottom (rows 24-31) as it is now
    for (y = 0; y < 8; y++)
        for (x = 0; x < 128; x++)
            SetPix(stripTile, x, y, GetPix(hbTile, x, ROW_NUMBERS + y));
    // rows 24-31 become plain interior rows (the numbers row)
    for (y = ROW_NUMBERS; y < 32; y++)
        for (x = 0; x < 128; x++)
            SetPix(hbTile, x, y, PlainPix(hbTile, x));
}

static void DrawFoeHpNumbers(u16 hbTile, s16 hp, s16 maxHp)
{
    u8 text[16];
    u8 *p;
    u8 color[3] = {2, 1, 3};
    u8 winId, x, y, right, w;
    u8 *tiles;
    struct WindowTemplate tmpl = {.bg = 0, .tilemapLeft = 0, .tilemapTop = 0, .width = 8, .height = 2, .paletteNum = 0, .baseBlock = 0};

    u8 work[16 * TILE_SIZE_4BPP];
    u8 t, r;
    // the numbers row = 8 copies of the plain interior row 16 (tile row 2, pixel row 0), built in RAM
    for (t = 0; t < 16; t++)
    {
        const u32 *src = (const u32 *)(OBJ_VRAM0 + (hbTile + (t >= 8 ? 32 : 0) + 16 + (t % 8)) * TILE_SIZE_4BPP);
        for (r = 0; r < 8; r++)
            ((u32 *)work)[t * 8 + r] = *src;
    }
    for (x = STATUS_X0; x < STATUS_X1; x++)
    {
        u8 c = PlainPix(hbTile, x);
        for (y = 0; y < 8; y++)
            BufSetPix(work, x, y, c);
    }
    p = ConvertIntToDecimalStringN(text, hp, STR_CONV_MODE_RIGHT_ALIGN, 3);
    *p++ = 0xBA;  // '/'
    ConvertIntToDecimalStringN(p, maxHp, STR_CONV_MODE_RIGHT_ALIGN, 3);
    winId = AddWindow(&tmpl);
    FillWindowPixelBuffer(winId, PIXEL_FILL(2));
    AddTextPrinterParameterized4(winId, FONT_SMALL, 0, 5, 0, 0, color, -1, text);
    tiles = (u8 *)GetWindowAttribute(winId, WINDOW_TILE_DATA);
    w = GetStringWidth(FONT_SMALL, text, 0);
    if (w > 63)
        w = 63;
    // right edge: last plain interior pixel of the box
    for (right = 127; right > 0 && GetPix(hbTile, right, ROW_PLAIN) != 2; right--)
        ;
    right -= 1;
    for (y = 0; y < 8; y++)
    {
        for (x = 0; x < w; x++)
        {
            u8 wy = 8 + y;
            u8 b = tiles[((wy / 8) * 8 + x / 8) * TILE_SIZE_4BPP + (wy % 8) * 4 + (x % 8) / 2];
            u8 c = (x & 1) ? (b >> 4) : (b & 0xF);
            BufSetPix(work, right - w + 1 + x, y, c);
        }
    }
    RemoveWindow(winId);
    CpuCopy32(work, (void *)(OBJ_VRAM0 + (hbTile + 24) * TILE_SIZE_4BPP), 8 * TILE_SIZE_4BPP);
    CpuCopy32(work + 8 * TILE_SIZE_4BPP, (void *)(OBJ_VRAM0 + (hbTile + 32 + 24) * TILE_SIZE_4BPP), 8 * TILE_SIZE_4BPP);
}

void JpSpriteCB_FoeHealthBar(struct Sprite *sprite)
{
    struct Sprite *hb, *strip, *other;
    u8 battler;
    u16 hbTile, stripTile;
    s16 hp, maxHp;

    JpSpriteCB_HealthBar(sprite);
    if (IsDoubleBattle() || (gBattleTypeFlags & BATTLE_TYPE_SAFARI))
        return;
    hb = &gSprites[sprite->data[5]];
    battler = hb->data[6];
    hbTile = hb->oam.tileNum;
    if (sprite->data[7] == 0 || gSprites[sprite->data[7] - 1].template != &sStripTemplate)
    {
        u8 a, b;
        if (GetSpriteTileStartByTag(TAG_JP_FOE_HP_STRIP) == 0xFFFF)
            LoadSpriteSheet(&sStripSheet);
        a = CreateSprite(&sStripTemplate, 0, 0, 1);
        b = CreateSprite(&sStripTemplate, 0, 0, 1);
        if (a == MAX_SPRITES || b == MAX_SPRITES)
            return;
        gSprites[b].oam.tileNum += 32;
        gSprites[a].sStripOther = b;
        gSprites[a].sLastHp = FOE_HP_NONE;
        sprite->data[7] = a + 1;
        sJpFoeHpShown[battler] = FOE_HP_NONE;
    }
    strip = &gSprites[sprite->data[7] - 1];
    other = &gSprites[strip->sStripOther];
    stripTile = strip->oam.tileNum;
    // (re)patch when the healthbox graphics were (re)loaded: the left edge of row 28 is still outside the box
    if (GetPix(hbTile, 1, 28) != GetPix(hbTile, 1, ROW_PLAIN))
    {
        PatchHealthbox(hbTile, stripTile);
        strip->sLastHp = FOE_HP_NONE;
    }
    hp = gBattleMons[battler].hp;
    if (sJpFoeHpShown[battler] != FOE_HP_NONE)
    {
        if (sJpFoeHpShown[battler] == hp && gBattleSpritesDataPtr->battleBars[battler].currValue == 0)
            sJpFoeHpShown[battler] = FOE_HP_NONE;
        else
            hp = sJpFoeHpShown[battler];
    }
    maxHp = gBattleMons[battler].maxHP;
    if (hp != strip->sLastHp || maxHp != strip->sLastMax)
    {
        DrawFoeHpNumbers(hbTile, hp, maxHp);
        strip->sLastHp = hp;
        strip->sLastMax = maxHp;
    }
    strip->x = hb->x;
    strip->y = hb->y + 32;
    strip->x2 = hb->x2;
    strip->y2 = hb->y2;
    strip->invisible = hb->invisible;
    strip->oam.priority = hb->oam.priority;
    other->x = hb->x + 64;
    other->y = strip->y;
    other->x2 = hb->x2;
    other->y2 = hb->y2;
    other->invisible = hb->invisible;
    other->oam.priority = hb->oam.priority;
}

