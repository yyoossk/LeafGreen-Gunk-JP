#include "global.h"
#include "gflib.h"
#include "list_menu.h"
#include "script.h"
#include "data.h"
#include "menu.h"
#include "fieldmap.h"
#include "pokedex.h"
#include "pokemon.h"
#include "region_map.h"
#include "sound.h"
#include "string_util.h"
#include "task.h"
#include "wild_encounter.h"
#include "constants/songs.h"
#include "constants/species.h"

// ずかんの さいしょの メニューに「いまいる ばしょ」：いまの マップで でる やせいの ポケモンを、
// くさむら・なみのり・いわくだき・つり ごとに ならべる。つかまえた ポケモンは くろ、みただけは はいいろ、
// みていない ポケモンは「？？？？？」。うえ・したで スクロール、A か B で もどる。
// JP Task_PokedexScreen の ListMenu_ProcessInput (0x0810377C) を JpDexTopMenuInput に つなぎかえる。

#define DEX_MODE_JP_HERE 15
#define JpSpeciesNames ((const u8 (*)[6])0x081FF4AC)   // 5 もじ ＋ おわり
#define ROW_H 16
#define ROWS_SHOWN 7
#define MAX_LINES 32

extern const u8 gJpText_DexHereTitle[];
extern const u8 gJpText_DexHereNone[];
extern const u8 gJpText_DexHereLand[];
extern const u8 gJpText_DexHereWater[];
extern const u8 gJpText_DexHereRock[];
extern const u8 gJpText_DexHereFish[];
extern const u8 gJpText_DexHereUnknown[];

// line: species (0 = blank), or a label: 0xF000 | section
struct JpHereLine { u16 a, b; };

static EWRAM_DATA bool8 sJpHereActive = FALSE;
static EWRAM_DATA u8 sJpHereScroll = 0;
static EWRAM_DATA u8 sJpHereNumLines = 0;

static const u8 *const sSectionNames[] = {gJpText_DexHereLand, gJpText_DexHereWater, gJpText_DexHereRock, gJpText_DexHereFish};

// 151匹揃う版は ひとつの マップに ヘッダが 2つ（ファイアレッド・リーフグリーン）あるので、あう ものを ぜんぶ あわせる

static void Collect(u16 sJpHereSpecies[4][16], u8 *sJpHereCount, u8 section, const struct WildPokemonInfo *info, u8 count)
{
    u8 i, j;

    if (info == NULL || info->wildPokemon == NULL)
        return;
    for (i = 0; i < count; i++)
    {
        u16 sp = info->wildPokemon[i].species;
        for (j = 0; j < sJpHereCount[section]; j++)
            if (sJpHereSpecies[section][j] == sp)
                break;
        if (j == sJpHereCount[section] && sp != SPECIES_NONE && sJpHereCount[section] < 16)
            sJpHereSpecies[section][sJpHereCount[section]++] = sp;
    }
}

static void BuildLines(struct JpHereLine *sJpHereLines)
{
    u16 sJpHereSpecies[4][16];
    u8 sJpHereCount[4];
    u16 i;
    u8 sec, k;

    for (sec = 0; sec < 4; sec++)
        sJpHereCount[sec] = 0;
    for (i = 0; gWildMonHeaders[i].mapGroup != 0xFF; i++)
    {
        const struct WildPokemonHeader *h = &gWildMonHeaders[i];
        if (h->mapGroup != gSaveBlock1Ptr->location.mapGroup || h->mapNum != gSaveBlock1Ptr->location.mapNum)
            continue;
        Collect(sJpHereSpecies, sJpHereCount, 0, h->landMonsInfo, 12);
        Collect(sJpHereSpecies, sJpHereCount, 1, h->waterMonsInfo, 5);
        Collect(sJpHereSpecies, sJpHereCount, 2, h->rockSmashMonsInfo, 5);
        Collect(sJpHereSpecies, sJpHereCount, 3, h->fishingMonsInfo, 10);
    }
    sJpHereNumLines = 0;
    for (sec = 0; sec < 4; sec++)
    {
        if (sJpHereCount[sec] == 0 || sJpHereNumLines >= MAX_LINES)
            continue;
        sJpHereLines[sJpHereNumLines].a = 0xF000 | sec;
        sJpHereLines[sJpHereNumLines].b = 0;
        sJpHereNumLines++;
        for (k = 0; k < sJpHereCount[sec] && sJpHereNumLines < MAX_LINES; k += 2)
        {
            sJpHereLines[sJpHereNumLines].a = sJpHereSpecies[sec][k];
            sJpHereLines[sJpHereNumLines].b = (k + 1 < sJpHereCount[sec]) ? sJpHereSpecies[sec][k + 1] : 0;
            sJpHereNumLines++;
        }
    }
}

struct JpHereColors { u8 normal[3]; u8 gray[3]; u8 label[3]; };
// ずかんの パレット：1 くろ・3 かげ、12 はいいろ・11 うすい かげ、14 あか（「さくいん」と おなじ）
static const struct JpHereColors sDexColors = {{0, 1, 3}, {0, 12, 11}, {0, 14, 15}};
// フィールドの まど（パレット 15）：2 こい はいいろ・3 うすい はいいろ、4 あか
static const struct JpHereColors sFieldColors = {{1, 2, 3}, {1, 3, 1}, {1, 4, 5}};

static void PrintMon(u8 win, const struct JpHereColors *c, u16 species, u8 x, u8 y)
{
    u16 dexNum = SpeciesToNationalPokedexNum(species);

    if (GetSetPokedexFlag(dexNum, FLAG_GET_CAUGHT))
        AddTextPrinterParameterized4(win, FONT_NORMAL, x, y, 0, 0, c->normal, TEXT_SKIP_DRAW, JpSpeciesNames[species]);
    else if (GetSetPokedexFlag(dexNum, FLAG_GET_SEEN))
        AddTextPrinterParameterized4(win, FONT_NORMAL, x, y, 0, 0, c->gray, TEXT_SKIP_DRAW, JpSpeciesNames[species]);
    else
        AddTextPrinterParameterized4(win, FONT_NORMAL, x, y, 0, 0, c->gray, TEXT_SKIP_DRAW, gJpText_DexHereUnknown);
}

static void DrawList(u8 win, const struct JpHereColors *c, u8 fill)
{
    struct JpHereLine sJpHereLines[MAX_LINES];
    u8 name[32];
    u8 i;

    BuildLines(sJpHereLines);
    FillWindowPixelBuffer(win, PIXEL_FILL(fill));
    GetMapName(name, gMapHeader.regionMapSectionId, 0);
    StringCopy(gStringVar4, name);
    StringAppend(gStringVar4, gJpText_DexHereTitle);
    AddTextPrinterParameterized4(win, FONT_NORMAL, 4, 2, 0, 0, c->normal, TEXT_SKIP_DRAW, gStringVar4);
    if (sJpHereNumLines == 0)
        AddTextPrinterParameterized4(win, FONT_NORMAL, 4, 2 + ROW_H * 2, 0, 0, c->normal, TEXT_SKIP_DRAW, gJpText_DexHereNone);
    for (i = 0; i < ROWS_SHOWN && sJpHereScroll + i < sJpHereNumLines; i++)
    {
        struct JpHereLine *l = &sJpHereLines[sJpHereScroll + i];
        u8 y = 2 + ROW_H * (i + 1);
        if ((l->a & 0xF000) == 0xF000)
            AddTextPrinterParameterized4(win, FONT_NORMAL, 4, y, 0, 0, c->label, TEXT_SKIP_DRAW, sSectionNames[l->a & 3]);
        else
        {
            PrintMon(win, c, l->a, 16, y);
            if (l->b != 0)
                PrintMon(win, c, l->b, 88, y);
        }
    }
    CopyWindowToVram(win, COPYWIN_FULL);
}

static void Draw(u8 win)
{
    DrawList(win, &sDexColors, 0);
}

static u8 ListWindow(u8 listTaskId)
{
    struct ListMenu *list = (struct ListMenu *)gTasks[listTaskId].data;
    return list->template.windowId;
}

s32 JpDexTopMenuInput(u8 listTaskId)
{
    s32 r;

    if (sJpHereActive)
    {
        if (JOY_NEW(A_BUTTON | B_BUTTON))
        {
            PlaySE(SE_SELECT);
            sJpHereActive = FALSE;
            RedrawListMenu(listTaskId);
        }
        else if (JOY_REPT(DPAD_DOWN) && sJpHereScroll + ROWS_SHOWN < sJpHereNumLines)
        {
            PlaySE(SE_SELECT);
            sJpHereScroll++;
            Draw(ListWindow(listTaskId));
        }
        else if (JOY_REPT(DPAD_UP) && sJpHereScroll > 0)
        {
            PlaySE(SE_SELECT);
            sJpHereScroll--;
            Draw(ListWindow(listTaskId));
        }
        gMain.newKeys = 0;
        gMain.newAndRepeatedKeys = 0;
        return LIST_NOTHING_CHOSEN;
    }

    r = ListMenu_ProcessInput(listTaskId);
    if (r == DEX_MODE_JP_HERE && JOY_NEW(A_BUTTON))
    {
        PlaySE(SE_SELECT);
        sJpHereScroll = 0;
        sJpHereActive = TRUE;
        Draw(ListWindow(listTaskId));
        gMain.newKeys = 0;
        return LIST_NOTHING_CHOSEN;
    }
    return r;
}

// ---- スタートメニューの「このばしょ」：フィールドに まどを だし、とじたら スタートメニューに もどる
#define JpStartMenuExitCallback ((bool8 (*)(void))0x0806ECA9)
#define JpShowStartMenu         ((void (*)(void))0x0806E9C5)
void JpSetStdWindowBorderStyle(u8 windowId, bool8 copyToVram);
void JpScheduleBgCopyTilemapToVram(u8 bg);
#define JpClearStdWindowAndFrameToTransparent ((void (*)(u8, bool8))0x0810FF6D)
void FreezeObjectEvents(void);

static const struct WindowTemplate sJpHereFieldWindow = {
    .bg = 0, .tilemapLeft = 2, .tilemapTop = 1, .width = 26, .height = 16, .paletteNum = 15, .baseBlock = 0x038
};

static void Task_JpHereField(u8 taskId)
{
    u8 win = gTasks[taskId].data[0];

    if (JOY_NEW(A_BUTTON | B_BUTTON))
    {
        PlaySE(SE_SELECT);
        JpClearStdWindowAndFrameToTransparent(win, TRUE);
        ClearWindowTilemap(win);
        RemoveWindow(win);
        JpScheduleBgCopyTilemapToVram(0);
        DestroyTask(taskId);
        JpShowStartMenu();
    }
    else if (JOY_REPT(DPAD_DOWN) && sJpHereScroll + ROWS_SHOWN < sJpHereNumLines)
    {
        PlaySE(SE_SELECT);
        sJpHereScroll++;
        DrawList(win, &sFieldColors, 1);
    }
    else if (JOY_REPT(DPAD_UP) && sJpHereScroll > 0)
    {
        PlaySE(SE_SELECT);
        sJpHereScroll--;
        DrawList(win, &sFieldColors, 1);
    }
}

bool8 JpStartMenuHereCallback(void)
{
    u8 win;

    JpStartMenuExitCallback();
    FreezeObjectEvents();
    LockPlayerFieldControls();
    win = AddWindow(&sJpHereFieldWindow);
    PutWindowTilemap(win);
    JpSetStdWindowBorderStyle(win, FALSE);
    sJpHereScroll = 0;
    DrawList(win, &sFieldColors, 1);
    JpScheduleBgCopyTilemapToVram(0);
    gTasks[CreateTask(Task_JpHereField, 80)].data[0] = win;
    return TRUE;
}
