#include "global.h"
#include "gflib.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "field_camera.h"
#include "field_control_avatar.h"
#include "field_effect.h"
#include "field_effect_helpers.h"
#include "field_player_avatar.h"
#include "field_weather.h"
#include "fieldmap.h"
#include "metatile_behavior.h"
#include "overworld.h"
#include "quest_log.h"
#include "script.h"
#include "gunk_follower.h"
#include "constants/event_object_movement.h"
#include "constants/event_objects.h"
#include "constants/species.h"

// statics of the original file (resolved to the Japanese ROM's addresses)
u8 InitObjectEventStateFromTemplate(const struct ObjectEventTemplate *template, u8 mapNum, u8 mapGroup);
void UpdateObjectEventVisibility(struct ObjectEvent *, struct Sprite *);
void RemoveObjectEventIfOutsideView(struct ObjectEvent *);
void SetPlayerAvatarObjectEventIdAndObjectId(u8, u8);
void ResetObjectEventFldEffData(struct ObjectEvent *);
void CopyObjectGraphicsInfoToSpriteTemplate_WithMovementType(u16 graphicsId, u16 movementType, struct SpriteTemplate *spriteTemplate, const struct SubspriteTable **subspriteTables);
u8 GetMoveDirectionFastAnimNum(u8 direction);
extern const union AnimCmd *const sAnimTable_Standard[];
extern const struct SubspriteTable gObjectEventSpriteOamTables_32x32[];

#define OBJ_EVENT_PAL_TAG_GUNK_FOLLOWER 0x1150
#define OBJ_EVENT_PAL_TAG_NONE 0x11FF
extern const struct ObjectEventGraphicsInfo *const gObjectEventGraphicsInfoPointers[];
void InitNpcForRunSlow(struct ObjectEvent *objectEvent, struct Sprite *sprite, u8 direction);
void SetStepAnimHandleAlternation(struct ObjectEvent *objectEvent, struct Sprite *sprite, u8 animNum);
u8 GetRunningDirectionAnimNum(u8 direction);

struct GunkFollowerGfx
{
    const u32 *pic;
    const u16 *pal;
    const u16 *shinyPal;
};
#include "../data/gunk_followers.h"

#define GUNK_FOLLOWER_FRAME_SIZE (32 * 32 / 2)

static EWRAM_DATA struct SpriteFrameImage sGunkFollowerFrames[9] = {0};
static EWRAM_DATA struct ObjectEventGraphicsInfo sGunkFollowerGfxInfo = {0};
static EWRAM_DATA const u16 *sGunkFollowerPalette = NULL;

bool8 SetGunkFollowerGraphics(u16 species, bool8 shiny)
{
    static const u8 sFrameOfImage[9] = {0, 2, 4, 1, 1, 3, 3, 5, 5};
    u8 i;

    if (species == SPECIES_NONE || species >= NUM_SPECIES || sGunkFollowerGfx[species].pic == NULL)
        return FALSE;
    for (i = 0; i < ARRAY_COUNT(sGunkFollowerFrames); i++)
    {
        sGunkFollowerFrames[i].data = (const u8 *)sGunkFollowerGfx[species].pic + sFrameOfImage[i] * GUNK_FOLLOWER_FRAME_SIZE;
        sGunkFollowerFrames[i].size = GUNK_FOLLOWER_FRAME_SIZE;
    }
    sGunkFollowerGfxInfo.tileTag = TAG_NONE;
    sGunkFollowerGfxInfo.paletteTag = OBJ_EVENT_PAL_TAG_GUNK_FOLLOWER;
    sGunkFollowerGfxInfo.reflectionPaletteTag = OBJ_EVENT_PAL_TAG_NONE;
    sGunkFollowerGfxInfo.size = GUNK_FOLLOWER_FRAME_SIZE;
    sGunkFollowerGfxInfo.width = 32;
    sGunkFollowerGfxInfo.height = 32;
    sGunkFollowerGfxInfo.paletteSlot = PALSLOT_NPC_1;
    sGunkFollowerGfxInfo.shadowSize = SHADOW_SIZE_M;
    sGunkFollowerGfxInfo.inanimate = FALSE;
    sGunkFollowerGfxInfo.disableReflectionPaletteLoad = TRUE;
    sGunkFollowerGfxInfo.tracks = TRACKS_FOOT;
    sGunkFollowerGfxInfo.oam = &gObjectEventBaseOam_32x32;
    sGunkFollowerGfxInfo.subspriteTables = gObjectEventSpriteOamTables_32x32;
    sGunkFollowerGfxInfo.anims = sAnimTable_Standard;
    sGunkFollowerGfxInfo.images = sGunkFollowerFrames;
    sGunkFollowerGfxInfo.affineAnims = gDummySpriteAffineAnimTable;
    sGunkFollowerPalette = shiny ? sGunkFollowerGfx[species].shinyPal : sGunkFollowerGfx[species].pal;
    return TRUE;
}

static u8 LoadGunkFollowerPalette(void)
{
    struct SpritePalette palette;
    u8 paletteNum;

    FreeSpritePaletteByTag(OBJ_EVENT_PAL_TAG_GUNK_FOLLOWER);
    palette.data = sGunkFollowerPalette;
    palette.tag = OBJ_EVENT_PAL_TAG_GUNK_FOLLOWER;
    paletteNum = LoadSpritePalette(&palette);
    if (paletteNum == 0xFF)
        return PALSLOT_NPC_1;
    ApplyGlobalFieldPaletteTint(paletteNum);
    UpdateSpritePaletteWithWeather(paletteNum);
    return paletteNum;
}

// Vanilla bug: sObjectEventSpritePalettes ends with {} (tag 0), not OBJ_EVENT_PAL_TAG_NONE, so looking up an unknown
// tag never stops (the shop's map view hangs on the follower's palette). Stop at the real end, and load the follower's own palette.
extern const struct SpritePalette gJpObjectEventSpritePalettes[];
u8 FindObjectEventPaletteIndexByTag(u16 tag)
{
    u8 i;

    for (i = 0; gJpObjectEventSpritePalettes[i].data != NULL && gJpObjectEventSpritePalettes[i].tag != OBJ_EVENT_PAL_TAG_NONE; i++)
    {
        if (gJpObjectEventSpritePalettes[i].tag == tag)
            return i;
    }
    return 0xFF;
}

void LoadObjectEventPalette(u16 paletteTag)
{
    u8 i;

    if (paletteTag == OBJ_EVENT_PAL_TAG_GUNK_FOLLOWER)
    {
        if (sGunkFollowerPalette != NULL && IndexOfSpritePaletteTag(paletteTag) == 0xFF)
            LoadGunkFollowerPalette();
        return;
    }
    i = FindObjectEventPaletteIndexByTag(paletteTag);
    if (i != 0xFF && IndexOfSpritePaletteTag(gJpObjectEventSpritePalettes[i].tag) == 0xFF)
        LoadSpritePalette(&gJpObjectEventSpritePalettes[i]);
}

// FRLG+ Master Trainer overworld sprites (gfx 160-169); filled in by tools/patch_port.py
#define JP_MASTER_GFX_FIRST 160
extern const struct ObjectEventGraphicsInfo *const gJpMasterGfxPtrs[12];   // data/hooks/master_trainers.s
void JpMaster_AdjustSpawn(struct ObjectEvent *objectEvent, const struct ObjectEventTemplate *template, struct SpriteTemplate *spriteTemplate);

const struct ObjectEventGraphicsInfo *GetObjectEventGraphicsInfo(u8 graphicsId)
{
    if (graphicsId >= OBJ_EVENT_GFX_VARS)
        graphicsId = VarGetObjectEventGraphicsId(graphicsId - OBJ_EVENT_GFX_VARS);

    if (graphicsId == OBJ_EVENT_GFX_GUNK_FOLLOWER && sGunkFollowerGfxInfo.images != NULL)
        return &sGunkFollowerGfxInfo;

    if (graphicsId >= JP_MASTER_GFX_FIRST && graphicsId < JP_MASTER_GFX_FIRST + 12)
        return gJpMasterGfxPtrs[graphicsId - JP_MASTER_GFX_FIRST];

    if (graphicsId >= NUM_OBJ_EVENT_GFX)
        graphicsId = OBJ_EVENT_GFX_LITTLE_BOY;

    return gObjectEventGraphicsInfoPointers[graphicsId];
}

u8 TrySetupObjectEventSprite(const struct ObjectEventTemplate *objectEventTemplate, struct SpriteTemplate *spriteTemplate, u8 mapNum, u8 mapGroup, s16 cameraX, s16 cameraY)
{
    u8 spriteId;
    u8 objectEventId;
    struct Sprite *sprite;
    struct ObjectEvent *objectEvent;
    const struct ObjectEventGraphicsInfo *graphicsInfo;

    objectEventId = InitObjectEventStateFromTemplate(objectEventTemplate, mapNum, mapGroup);
    if (objectEventId == OBJECT_EVENTS_COUNT)
        return OBJECT_EVENTS_COUNT;

    objectEvent = &gObjectEvents[objectEventId];
    JpMaster_AdjustSpawn(objectEvent, objectEventTemplate, spriteTemplate);
    graphicsInfo = GetObjectEventGraphicsInfo(objectEvent->graphicsId);
    if (graphicsInfo->paletteSlot == PALSLOT_PLAYER)
        LoadPlayerObjectReflectionPalette(graphicsInfo->paletteTag, graphicsInfo->paletteSlot);
    else if (graphicsInfo->paletteSlot == PALSLOT_NPC_SPECIAL)
        LoadSpecialObjectReflectionPalette(graphicsInfo->paletteTag, graphicsInfo->paletteSlot);

    if (objectEvent->movementType == MOVEMENT_TYPE_INVISIBLE)
        objectEvent->invisible = TRUE;

    *(u16 *)&spriteTemplate->paletteTag = TAG_NONE;
    spriteId = CreateSprite(spriteTemplate, 0, 0, 0);
    if (spriteId == MAX_SPRITES)
    {
        gObjectEvents[objectEventId].active = FALSE;
        return OBJECT_EVENTS_COUNT;
    }

    sprite = &gSprites[spriteId];
    GetMapCoordsFromSpritePos(objectEvent->currentCoords.x + cameraX, objectEvent->currentCoords.y + cameraY, &sprite->x, &sprite->y);
    sprite->centerToCornerVecX = -(graphicsInfo->width >> 1);
    sprite->centerToCornerVecY = -(graphicsInfo->height >> 1);
    sprite->x += 8;
    sprite->y += 16 + sprite->centerToCornerVecY;
    sprite->oam.paletteNum = graphicsInfo->paletteSlot;
    if (objectEvent->graphicsId == OBJ_EVENT_GFX_GUNK_FOLLOWER)
        sprite->oam.paletteNum = LoadGunkFollowerPalette();
    sprite->coordOffsetEnabled = TRUE;
    sprite->data[0] = objectEventId;
    objectEvent->spriteId = spriteId;
    objectEvent->inanimate = graphicsInfo->inanimate;
    if (!objectEvent->inanimate)
        StartSpriteAnim(sprite, GetFaceDirectionAnimNum(objectEvent->facingDirection));

    SetObjectSubpriorityByElevation(objectEvent->previousElevation, sprite, 1);
    UpdateObjectEventVisibility(objectEvent, sprite);
    return objectEventId;
}

void RemoveObjectEventsOutsideView(void)
{
    u8 i, j;
    bool8 isActiveLinkPlayer;

    for (i = 0; i < OBJECT_EVENTS_COUNT; i++)
    {
        for (j = 0, isActiveLinkPlayer = FALSE; j < 4; j++)
        {
            if (gLinkPlayerObjectEvents[j].active && i == gLinkPlayerObjectEvents[j].objEventId)
                isActiveLinkPlayer = TRUE;
        }
        if (IsFollowerActive() && i == GetFollowerObjEventId())
            isActiveLinkPlayer = TRUE;
        if (!isActiveLinkPlayer)
        {
            struct ObjectEvent *objectEvent = &gObjectEvents[i];

            if (objectEvent->active && !objectEvent->isPlayer)
                RemoveObjectEventIfOutsideView(objectEvent);
        }
    }
}

void SpawnObjectEventOnReturnToField(u8 objectEventId, s16 x, s16 y)
{
    u8 spriteId;
    struct Sprite *sprite;
    struct ObjectEvent *objectEvent;
    struct SpriteTemplate spriteTemplate;
    struct SpriteFrameImage spriteFrameImage;
    const struct SubspriteTable *subspriteTables;
    const struct ObjectEventGraphicsInfo *graphicsInfo;

    for (spriteId = 0; spriteId < 4; spriteId++)
    {
        if (gLinkPlayerObjectEvents[spriteId].active && objectEventId == gLinkPlayerObjectEvents[spriteId].objEventId)
            return;
    }

    objectEvent = &gObjectEvents[objectEventId];
    subspriteTables = NULL;
    graphicsInfo = GetObjectEventGraphicsInfo(objectEvent->graphicsId);
    spriteFrameImage.size = graphicsInfo->size;
    CopyObjectGraphicsInfoToSpriteTemplate_WithMovementType(objectEvent->graphicsId, objectEvent->movementType, &spriteTemplate, &subspriteTables);
    spriteTemplate.images = &spriteFrameImage;

    *(u16 *)&spriteTemplate.paletteTag = TAG_NONE;
    if (graphicsInfo->paletteSlot == PALSLOT_PLAYER)
        LoadPlayerObjectReflectionPalette(graphicsInfo->paletteTag, graphicsInfo->paletteSlot);

    if (graphicsInfo->paletteSlot >= PALSLOT_NPC_SPECIAL)
        LoadSpecialObjectReflectionPalette(graphicsInfo->paletteTag, graphicsInfo->paletteSlot);

    *(u16 *)&spriteTemplate.paletteTag = TAG_NONE;
    spriteId = CreateSprite(&spriteTemplate, 0, 0, 0);
    if (spriteId != MAX_SPRITES)
    {
        sprite = &gSprites[spriteId];
        GetMapCoordsFromSpritePos(x + objectEvent->currentCoords.x, y + objectEvent->currentCoords.y, &sprite->x, &sprite->y);
        sprite->centerToCornerVecX = -(graphicsInfo->width >> 1);
        sprite->centerToCornerVecY = -(graphicsInfo->height >> 1);
        sprite->x += 8;
        sprite->y += 16 + sprite->centerToCornerVecY;
        sprite->images = graphicsInfo->images;
        if (objectEvent->movementType == MOVEMENT_TYPE_PLAYER)
        {
            SetPlayerAvatarObjectEventIdAndObjectId(objectEventId, spriteId);
            objectEvent->warpArrowSpriteId = CreateWarpArrowSprite();
        }
        if (subspriteTables != NULL)
            SetSubspriteTables(sprite, subspriteTables);

        sprite->oam.paletteNum = graphicsInfo->paletteSlot;
        if (objectEvent->graphicsId == OBJ_EVENT_GFX_GUNK_FOLLOWER)
            sprite->oam.paletteNum = LoadGunkFollowerPalette();
        sprite->coordOffsetEnabled = TRUE;
        sprite->data[0] = objectEventId;
        objectEvent->spriteId = spriteId;
        if (!objectEvent->inanimate && objectEvent->movementType != MOVEMENT_TYPE_PLAYER)
            StartSpriteAnim(sprite, GetFaceDirectionAnimNum(objectEvent->facingDirection));

        ResetObjectEventFldEffData(objectEvent);
        SetObjectSubpriorityByElevation(objectEvent->previousElevation, sprite, 1);
    }
}

void ObjectEventSetGraphicsId(struct ObjectEvent *objectEvent, u8 graphicsId)
{
    const struct ObjectEventGraphicsInfo *graphicsInfo;
    struct Sprite *sprite;
    u8 var;
    u8 var3;

    graphicsInfo = GetObjectEventGraphicsInfo(graphicsId);
    sprite = &gSprites[objectEvent->spriteId];
    if (graphicsInfo->paletteSlot == PALSLOT_PLAYER)
        PatchObjectPalette(graphicsInfo->paletteTag, graphicsInfo->paletteSlot);

    if (graphicsInfo->paletteSlot == PALSLOT_NPC_SPECIAL)
        LoadSpecialObjectReflectionPalette(graphicsInfo->paletteTag, graphicsInfo->paletteSlot);

    var = sprite->images->size / TILE_SIZE_4BPP;
    if (!sprite->usingSheet)
        FreeSpriteTilesIfNotUsingSheet(sprite);
    sprite->oam.shape = graphicsInfo->oam->shape;
    sprite->oam.size = graphicsInfo->oam->size;
    sprite->images = graphicsInfo->images;
    sprite->anims = graphicsInfo->anims;
    sprite->subspriteTables = graphicsInfo->subspriteTables;
    sprite->oam.paletteNum = graphicsInfo->paletteSlot;
    if (objectEvent->graphicsId == OBJ_EVENT_GFX_GUNK_FOLLOWER)
        sprite->oam.paletteNum = LoadGunkFollowerPalette();
    if (!sprite->usingSheet)
    {
        s32 var2;
        var3 = sprite->images->size / TILE_SIZE_4BPP;
        var2 = AllocSpriteTiles(var3);
        if (var2 == -1)
            var2 = AllocSpriteTiles(var);
        sprite->oam.tileNum = var2;
    }
    objectEvent->inanimate = graphicsInfo->inanimate;
    objectEvent->graphicsId = graphicsId;
    SetSpritePosToMapCoords(objectEvent->currentCoords.x, objectEvent->currentCoords.y, &sprite->x, &sprite->y);
    sprite->centerToCornerVecX = -(graphicsInfo->width >> 1);
    sprite->centerToCornerVecY = -(graphicsInfo->height >> 1);
    sprite->x += 8;
    sprite->y += 16 + sprite->centerToCornerVecY;
    if (objectEvent->trackedByCamera)
        CameraObjectReset1();
}

void InitRunSlow(struct ObjectEvent *objectEvent, struct Sprite *sprite, u8 direction)
{
    InitNpcForRunSlow(objectEvent, sprite, direction);
    if (!objectEvent->isPlayer)
        SetStepAnimHandleAlternation(objectEvent, sprite, GetMoveDirectionFastAnimNum(objectEvent->facingDirection));
    else
        SetStepAnimHandleAlternation(objectEvent, sprite, GetRunningDirectionAnimNum(objectEvent->facingDirection));
}
