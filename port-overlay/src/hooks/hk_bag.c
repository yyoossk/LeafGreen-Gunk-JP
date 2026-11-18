#include "global.h"
#include "item.h"
#include "menu_indicators.h"
#include "list_menu.h"
#include "menu_indicators.h"
#include "menu.h"
#include "menu_helpers.h"
#include "new_menu_helpers.h"
#include "sound.h"
#include "sprite.h"
#include "task.h"
#include "bg.h"
#include "window.h"
#include "malloc.h"
#include "constants/items.h"
#include "constants/songs.h"
// FRLG+: two more bag pockets, くすり (medicine) and もちもの (held items).
//
// They live in SaveBlock1's unused 400 bytes at 0x348C. To leave the Japanese bag code alone, the new
// pockets take bag-menu indices 11 and 12 (pocket ids 12 and 13): every per-pocket array in the menu
// (cursorPos/itemsAbove, nItems/maxShowed) is indexed base + pocket, and with these indices none of
// them lands on another array's live entries. gBagMenuState moves to EWRAM with room for 13 entries,
// gBagPockets grows to 13 (5-10 unused), and the menu steps through the pockets in the order below.

#define JP_POCKET_MEDICINE   12
#define JP_POCKET_HELD_ITEMS 13
#define JP_NUM_POCKETS       13
#define BAG_MEDICINE_COUNT   40
#define BAG_HELD_ITEMS_COUNT 52
#define SB1_MEDICINE   0x348C
#define SB1_HELD_ITEMS 0x352C
#define SB1_BAG_FORMAT 0x3618
#define JP_BAG_FORMAT  0x31474142 // "BAG1"

struct JpBagStruct
{
    MainCallback bagCallback;
    u8 location;
    bool8 bagOpen;
    u16 pocket;
    u16 itemsAbove[3];
    u16 cursorPos[JP_NUM_POCKETS + 3]; // itemsAbove[11..12] overlap cursorPos[8..9], which no pocket uses
};

struct JpBagMenuAlloc
{
    MainCallback exitCB;
    u8 itemOriginalLocation;
    u8 pocketSwitchMode:4;
    u8 itemMenuIcon:2;
    u8 inhibitItemDescriptionPrint:2;
    u16 contextMenuSelectedItem;
    u8 pocketScrollArrowsTask;
    u8 pocketSwitchArrowsTask;
    u8 nItems[3];
    u8 maxShowed[3];
    u8 data[4];
    u8 extra[8]; // nItems[11..12] = 0x15-0x16, maxShowed[11..12] = 0x18-0x19 (alloc patched 20 -> 28)
};
#define BAG_NITEMS(p)    (((u8 *)sJpBagMenuDisplay)[0x0A + (p)])
#define BAG_MAXSHOWED(p) (((u8 *)sJpBagMenuDisplay)[0x0D + (p)])
#define BAG_ITEMSABOVE(p) (((u16 *)((u8 *)&gBagMenuState + 8))[p])
#define BAG_CURSORPOS(p)  (((u16 *)((u8 *)&gBagMenuState + 0xE))[p])

EWRAM_DATA struct JpBagStruct gBagMenuState = {0};
EWRAM_DATA struct BagPocket gBagPockets[JP_NUM_POCKETS] = {0};
static EWRAM_DATA u16 sBagOrderPos = 0;   // where the shown pocket is in sBagOrder, for the L/R arrows
static EWRAM_DATA struct ItemSlot sNoSlot = {0};

#define sJpBagMenuDisplay (*(struct JpBagMenuAlloc **)0x0203AC88)
#define sJpItemMenuIconSpriteIds ((u8 *)0x020397C4)

// the order the L/R buttons step through (menu indices)
static const u8 sBagOrder[] = {0, 11, 1, 12, 2};
#define BAG_ORDER_COUNT 5
static const u8 sJpText_Medicine[] = _("く　す　り");
static const u8 sJpText_HeldItems[] = _("も　ち　も　の");

// JP statics of item_menu.c / item_menu_icons.c
void JpDrawItemListRow(u8 row);
void JpBag_BuildListMenuTemplate(u8 pocket);
void JpBagDestroyPocketScrollArrowPair(void);
void JpCreatePocketScrollArrowPair(void);
bool8 JpBagIsTutorial(void);
void JpPocket_CalculateNItemsAndMaxShowed(u8 pocket);
void JpPocketCalculateInitialCursorPosAndItemsAbove(u8 pocket);
void JpBagPrintTextOnWin1CenteredColor0(const u8 *str, u8 unused);
void JpSpriteCB_BagVisualSwitchingPockets(struct Sprite *sprite);
void JpOpenContextMenu(u8 taskId);
void DestroyItemMenuIcon(u8 idx);
void BagPocketCompaction(struct ItemSlot *slots, u8 capacity);
extern const u8 *const gJpPocketNames[];   // the vanilla three names

static u8 OrderPos(u8 pocket)
{
    u8 i;
    for (i = 0; i < BAG_ORDER_COUNT; i++)
        if (sBagOrder[i] == pocket)
            return i;
    return 0;
}

static bool8 IsBagMenuPocket(u16 pocket)
{
    return pocket <= 2 || pocket == 11 || pocket == 12;
}

// ---------------------------------------------------------------- item.c
void SetBagPocketsPointers(void)
{
    u8 i;

    for (i = 0; i < JP_NUM_POCKETS; i++)
    {
        gBagPockets[i].itemSlots = &sNoSlot;
        gBagPockets[i].capacity = 0;
    }
    gBagPockets[POCKET_ITEMS - 1].itemSlots = gSaveBlock1Ptr->bagPocket_Items;
    gBagPockets[POCKET_ITEMS - 1].capacity = BAG_ITEMS_COUNT;
    gBagPockets[POCKET_KEY_ITEMS - 1].itemSlots = gSaveBlock1Ptr->bagPocket_KeyItems;
    gBagPockets[POCKET_KEY_ITEMS - 1].capacity = BAG_KEYITEMS_COUNT;
    gBagPockets[POCKET_POKE_BALLS - 1].itemSlots = gSaveBlock1Ptr->bagPocket_PokeBalls;
    gBagPockets[POCKET_POKE_BALLS - 1].capacity = BAG_POKEBALLS_COUNT;
    gBagPockets[POCKET_TM_CASE - 1].itemSlots = gSaveBlock1Ptr->bagPocket_TMHM;
    gBagPockets[POCKET_TM_CASE - 1].capacity = BAG_TMHM_COUNT;
    gBagPockets[POCKET_BERRY_POUCH - 1].itemSlots = gSaveBlock1Ptr->bagPocket_Berries;
    gBagPockets[POCKET_BERRY_POUCH - 1].capacity = BAG_BERRIES_COUNT;
    gBagPockets[JP_POCKET_MEDICINE - 1].itemSlots = (struct ItemSlot *)((u8 *)gSaveBlock1Ptr + SB1_MEDICINE);
    gBagPockets[JP_POCKET_MEDICINE - 1].capacity = BAG_MEDICINE_COUNT;
    gBagPockets[JP_POCKET_HELD_ITEMS - 1].itemSlots = (struct ItemSlot *)((u8 *)gSaveBlock1Ptr + SB1_HELD_ITEMS);
    gBagPockets[JP_POCKET_HELD_ITEMS - 1].capacity = BAG_HELD_ITEMS_COUNT;
}

static void XorPocket(struct BagPocket *p, u32 newKey, u32 oldKey)
{
    u8 j;
    for (j = 0; j < p->capacity; j++)
        p->itemSlots[j].quantity ^= (u16)(oldKey ^ newKey);
}

void ApplyNewEncryptionKeyToBagItems(u32 newKey)
{
    u32 oldKey = gSaveBlock2Ptr->encryptionKey;
    u8 i;

    for (i = 0; i < JP_NUM_POCKETS; i++)
        XorPocket(&gBagPockets[i], newKey, oldKey);
}

static void ClearSlots(struct ItemSlot *slots, u8 n)
{
    u8 i;
    for (i = 0; i < n; i++)
    {
        slots[i].itemId = ITEM_NONE;
        slots[i].quantity = 0 ^ (u16)gSaveBlock2Ptr->encryptionKey;
    }
}

void ClearBag(void)
{
    u8 i;

    for (i = 0; i < JP_NUM_POCKETS; i++)
        ClearSlots(gBagPockets[i].itemSlots, gBagPockets[i].capacity);
    *(u32 *)((u8 *)gSaveBlock1Ptr + SB1_BAG_FORMAT) = JP_BAG_FORMAT;
}

// An old save: medicine and held items still sit in the どうぐ pocket. Called from LoadGameSave.
void JpBag_Upgrade(void)
{
    struct ItemSlot *items = gSaveBlock1Ptr->bagPocket_Items;
    u8 i;

    if (*(u32 *)((u8 *)gSaveBlock1Ptr + SB1_BAG_FORMAT) == JP_BAG_FORMAT)
        return;
    SetBagPocketsPointers();
    ClearSlots(gBagPockets[JP_POCKET_MEDICINE - 1].itemSlots, BAG_MEDICINE_COUNT);
    ClearSlots(gBagPockets[JP_POCKET_HELD_ITEMS - 1].itemSlots, BAG_HELD_ITEMS_COUNT);
    for (i = 0; i < BAG_ITEMS_COUNT; i++)
    {
        u16 item = items[i].itemId;
        u8 pocket;

        if (item == ITEM_NONE)
            continue;
        pocket = ItemId_GetPocket(item);
        if (pocket == JP_POCKET_MEDICINE || pocket == JP_POCKET_HELD_ITEMS)
        {
            u16 qty = items[i].quantity ^ (u16)gSaveBlock2Ptr->encryptionKey;
            items[i].itemId = ITEM_NONE;
            items[i].quantity = 0 ^ (u16)gSaveBlock2Ptr->encryptionKey;
            AddBagItem(item, qty);
        }
    }
    BagPocketCompaction(items, BAG_ITEMS_COUNT);
    *(u32 *)((u8 *)gSaveBlock1Ptr + SB1_BAG_FORMAT) = JP_BAG_FORMAT;
}

// ---------------------------------------------------------------- item_menu.c
void ResetBagCursorPositions(void)
{
    u8 i;

    gBagMenuState.pocket = POCKET_ITEMS - 1;
    gBagMenuState.bagOpen = FALSE;
    for (i = 0; i < BAG_ORDER_COUNT; i++)
    {
        BAG_ITEMSABOVE(sBagOrder[i]) = 0;
        BAG_CURSORPOS(sBagOrder[i]) = 0;
    }
}

void All_CalculateNItemsAndMaxShowed(void)
{
    u8 i;

    if (!IsBagMenuPocket(gBagMenuState.pocket))
        gBagMenuState.pocket = POCKET_ITEMS - 1;
    for (i = 0; i < BAG_ORDER_COUNT; i++)
        JpPocket_CalculateNItemsAndMaxShowed(sBagOrder[i]);
}

void CalculateInitialCursorPosAndItemsAbove(void)
{
    u8 i;

    if (!IsBagMenuPocket(gBagMenuState.pocket))
        gBagMenuState.pocket = POCKET_ITEMS - 1;
    for (i = 0; i < BAG_ORDER_COUNT; i++)
        JpPocketCalculateInitialCursorPosAndItemsAbove(sBagOrder[i]);
}

void UpdatePocketScrollPositions(void)
{
    u8 k, i, j;

    for (k = 0; k < BAG_ORDER_COUNT; k++)
    {
        i = sBagOrder[k];
        if (BAG_ITEMSABOVE(i) > 3)
        {
            for (j = 0; j <= BAG_ITEMSABOVE(i) - 3; BAG_ITEMSABOVE(i)--, BAG_CURSORPOS(i)++, j++)
            {
                if (BAG_CURSORPOS(i) + BAG_MAXSHOWED(i) == BAG_NITEMS(i) + 1)
                    break;
            }
        }
    }
}

void PrintBagPocketName(void)
{
    const u8 *name;
    u8 xIndex = gBagMenuState.pocket;   // the JP printer takes the x position from a per-pocket table

    switch (gBagMenuState.pocket)
    {
    case 11: name = sJpText_Medicine; xIndex = 0; break;    // 5 characters, like ど　う　ぐ
    case 12: name = sJpText_HeldItems; xIndex = 1; break;   // 7 characters, like たいせつなもの
    default: name = gJpPocketNames[gBagMenuState.pocket]; break;
    }
    FillWindowPixelBuffer(2, PIXEL_FILL(0));
    JpBagPrintTextOnWin1CenteredColor0(name, xIndex);
}

// returns 1 for "previous pocket", 2 for "next pocket"
u8 ProcessPocketSwitchInput(u8 taskId, u8 pocketId)
{
    u8 lrState;
    u8 pos = OrderPos(pocketId);

    if (sJpBagMenuDisplay->pocketSwitchMode != 0)
        return 0;
    lrState = GetLRKeysPressed();
    if (JOY_NEW(DPAD_LEFT) || lrState == MENU_L_PRESSED)
    {
        if (pos == 0)
            return 0;
        PlaySE(SE_BAG_POCKET);
        return 1;
    }
    if (JOY_NEW(DPAD_RIGHT) || lrState == MENU_R_PRESSED)
    {
        if (pos >= BAG_ORDER_COUNT - 1)
            return 0;
        PlaySE(SE_BAG_POCKET);
        return 2;
    }
    return 0;
}

static u8 StepPocket(u8 pocket, s16 dir)
{
    s16 pos = OrderPos(pocket) + dir;
    if (pos < 0)
        pos = 0;
    if (pos >= BAG_ORDER_COUNT)
        pos = BAG_ORDER_COUNT - 1;
    return sBagOrder[pos];
}

// the bag picture has three looks; the new pockets use the どうぐ one
void SetBagVisualPocketId(u8 animNum)
{
    struct Sprite *sprite = &gSprites[sJpItemMenuIconSpriteIds[0]];

    if (animNum > 2)
        animNum = 0;
    sprite->y2 = -5;
    sprite->callback = JpSpriteCB_BagVisualSwitchingPockets;
    StartSpriteAnim(sprite, animNum);
}

#define tSwitchDir     data[11]
#define tSwitchCounter data[12]
#define tSwitchState   data[13]

void Task_AnimateSwitchPockets(u8 taskId);
void CreatePocketSwitchArrowPair(void);

void SwitchPockets(u8 taskId, s16 direction, bool16 a2)
{
    s16 *data = gTasks[taskId].data;

    tSwitchState = 0;
    tSwitchCounter = 0;
    tSwitchDir = direction;
    if (!a2)
    {
        ClearWindowTilemap(0);
        ClearWindowTilemap(1);
        ClearWindowTilemap(2);
        DestroyListMenuTask(data[0], &BAG_CURSORPOS(gBagMenuState.pocket), &BAG_ITEMSABOVE(gBagMenuState.pocket));
        ScheduleBgCopyTilemapToVram(0);
        DestroyItemMenuIcon(sJpBagMenuDisplay->itemMenuIcon ^ 1);
        JpBagDestroyPocketScrollArrowPair();
    }
    FillBgTilemapBufferRect_Palette0(1, 0x02D, 11, 1, 18, 12);
    ScheduleBgCopyTilemapToVram(1);
    SetBagVisualPocketId(StepPocket(gBagMenuState.pocket, direction));
    SetTaskFuncWithFollowupFunc(taskId, Task_AnimateSwitchPockets, gTasks[taskId].func);
}

void Task_AnimateSwitchPockets(u8 taskId)
{
    s16 *data = gTasks[taskId].data;

    if (!MenuHelpers_IsLinkActive() && !JpBagIsTutorial())
    {
        switch (ProcessPocketSwitchInput(taskId, StepPocket(gBagMenuState.pocket, tSwitchDir)))
        {
        case 1:
            gBagMenuState.pocket = StepPocket(gBagMenuState.pocket, tSwitchDir);
            SwitchTaskToFollowupFunc(taskId);
            SwitchPockets(taskId, -1, TRUE);
            return;
        case 2:
            gBagMenuState.pocket = StepPocket(gBagMenuState.pocket, tSwitchDir);
            SwitchTaskToFollowupFunc(taskId);
            SwitchPockets(taskId, 1, TRUE);
            return;
        }
    }
    switch (tSwitchState)
    {
    case 0:
        if (tSwitchCounter != SHRT_MAX)
        {
            tSwitchCounter++;
            JpDrawItemListRow(tSwitchCounter);
            if (tSwitchCounter == 12)
                tSwitchCounter = SHRT_MAX;
        }
        if (tSwitchCounter == SHRT_MAX)
            tSwitchState++;
        break;
    case 1:
        gBagMenuState.pocket = StepPocket(gBagMenuState.pocket, tSwitchDir);
        PrintBagPocketName();
        JpBag_BuildListMenuTemplate(gBagMenuState.pocket);
        data[0] = ListMenuInit(&gMultiuseListMenuTemplate, BAG_CURSORPOS(gBagMenuState.pocket), BAG_ITEMSABOVE(gBagMenuState.pocket));
        PutWindowTilemap(1);
        PutWindowTilemap(2);
        ScheduleBgCopyTilemapToVram(0);
        JpCreatePocketScrollArrowPair();
        CreatePocketSwitchArrowPair();
        SwitchTaskToFollowupFunc(taskId);
        break;
    }
}

static const struct ScrollArrowsTemplate sJpPocketSwitchArrowPairTemplate = {
    .firstArrowType = SCROLL_ARROW_LEFT,
    .firstX = 8,
    .firstY = 72,
    .secondArrowType = SCROLL_ARROW_RIGHT,
    .secondX = 72,
    .secondY = 72,
    .fullyUpThreshold = 0,
    .fullyDownThreshold = BAG_ORDER_COUNT - 1,
    .tileTag = 111,
    .palTag = 111,
    .palNum = 0,
};

void CreatePocketSwitchArrowPair(void)
{
    sBagOrderPos = OrderPos(gBagMenuState.pocket);
    if (sJpBagMenuDisplay->pocketSwitchMode != 1)
        sJpBagMenuDisplay->pocketSwitchArrowsTask = AddScrollIndicatorArrowPair(&sJpPocketSwitchArrowPairTemplate, &sBagOrderPos);
}

// The JP context menu only knows the three vanilla pockets; the new ones get the どうぐ pocket's menu.
void JpOpenContextMenuWrapper(u8 taskId)
{
    u16 pocket = gBagMenuState.pocket;

    if (pocket > 2)
        gBagMenuState.pocket = POCKET_ITEMS - 1;
    JpOpenContextMenu(taskId);
    gBagMenuState.pocket = pocket;
}

// The Pokédude / old man demos borrow the bag; the new pockets are put aside too.
struct JpBagSlots
{
    struct ItemSlot items[BAG_ITEMS_COUNT];
    struct ItemSlot keyItems[BAG_KEYITEMS_COUNT];
    struct ItemSlot pokeBalls[BAG_POKEBALLS_COUNT];
    struct ItemSlot medicine[BAG_MEDICINE_COUNT];
    struct ItemSlot heldItems[BAG_HELD_ITEMS_COUNT];
    u16 itemsAbove[JP_NUM_POCKETS];
    u16 cursorPos[JP_NUM_POCKETS];
    u16 registeredItem;
    u16 pocket;
};
#define sJpBackupPlayerBag (*(struct JpBagSlots **)0x0203ACA4)

void BackUpPlayerBag(void)
{
    struct JpBagSlots *b;
    u8 k, i;

    b = sJpBackupPlayerBag = AllocZeroed(sizeof(struct JpBagSlots));
    memcpy(b->items, gSaveBlock1Ptr->bagPocket_Items, sizeof(b->items));
    memcpy(b->keyItems, gSaveBlock1Ptr->bagPocket_KeyItems, sizeof(b->keyItems));
    memcpy(b->pokeBalls, gSaveBlock1Ptr->bagPocket_PokeBalls, sizeof(b->pokeBalls));
    memcpy(b->medicine, gBagPockets[JP_POCKET_MEDICINE - 1].itemSlots, sizeof(b->medicine));
    memcpy(b->heldItems, gBagPockets[JP_POCKET_HELD_ITEMS - 1].itemSlots, sizeof(b->heldItems));
    b->registeredItem = gSaveBlock1Ptr->registeredItem;
    b->pocket = gBagMenuState.pocket;
    for (k = 0; k < BAG_ORDER_COUNT; k++)
    {
        i = sBagOrder[k];
        b->itemsAbove[i] = BAG_ITEMSABOVE(i);
        b->cursorPos[i] = BAG_CURSORPOS(i);
    }
    ClearSlots(gSaveBlock1Ptr->bagPocket_Items, BAG_ITEMS_COUNT);
    ClearSlots(gSaveBlock1Ptr->bagPocket_KeyItems, BAG_KEYITEMS_COUNT);
    ClearSlots(gSaveBlock1Ptr->bagPocket_PokeBalls, BAG_POKEBALLS_COUNT);
    ClearSlots(gBagPockets[JP_POCKET_MEDICINE - 1].itemSlots, BAG_MEDICINE_COUNT);
    ClearSlots(gBagPockets[JP_POCKET_HELD_ITEMS - 1].itemSlots, BAG_HELD_ITEMS_COUNT);
    gSaveBlock1Ptr->registeredItem = ITEM_NONE;
    ResetBagCursorPositions();
}

void RestorePlayerBag(void)
{
    struct JpBagSlots *b = sJpBackupPlayerBag;
    u8 k, i;

    memcpy(gSaveBlock1Ptr->bagPocket_Items, b->items, sizeof(b->items));
    memcpy(gSaveBlock1Ptr->bagPocket_KeyItems, b->keyItems, sizeof(b->keyItems));
    memcpy(gSaveBlock1Ptr->bagPocket_PokeBalls, b->pokeBalls, sizeof(b->pokeBalls));
    memcpy(gBagPockets[JP_POCKET_MEDICINE - 1].itemSlots, b->medicine, sizeof(b->medicine));
    memcpy(gBagPockets[JP_POCKET_HELD_ITEMS - 1].itemSlots, b->heldItems, sizeof(b->heldItems));
    gSaveBlock1Ptr->registeredItem = b->registeredItem;
    gBagMenuState.pocket = b->pocket;
    for (k = 0; k < BAG_ORDER_COUNT; k++)
    {
        i = sBagOrder[k];
        BAG_ITEMSABOVE(i) = b->itemsAbove[i];
        BAG_CURSORPOS(i) = b->cursorPos[i];
    }
    Free(b);
}
