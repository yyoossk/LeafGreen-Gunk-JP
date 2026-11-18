#include "global.h"
#include "battle_setup.h"
#include "event_object_movement.h"
#include "field_effect.h"
#include "field_player_avatar.h"
#include "quest_log.h"
#include "script.h"
#include "task.h"
#include "util.h"
#include "constants/battle_setup.h"
#include "constants/event_object_movement.h"
#include "constants/event_objects.h"
#include "constants/trainer_types.h"
#include "trainer_see.h"

void SpriteCB_TrainerIcons(struct Sprite *sprite);
void SetIconSpriteData(struct Sprite *sprite, u16 fldEffId, u8 spriteAnimNum);

static const u16 sGfx_GunkEmoticons[] = INCBIN_U16("graphics/misc/emoticons_gunk.4bpp");

static const struct OamData sOamData_GunkEmoticons = {
    .y = 0,
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(16x16),
    .x = 0,
    .matrixNum = 0,
    .size = SPRITE_SIZE(16x16),
    .tileNum = 0,
    .priority = 1,
    .paletteNum = 0,
    .affineParam = 0,
};

static const struct SpriteFrameImage sSpriteImages_GunkEmoticons[] =
{
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 0),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 1),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 2),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 6),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 7),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 8),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 3),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 4),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 5),
    overworld_frame(sGfx_GunkEmoticons, 2, 2,  9),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 10),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 11),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 12),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 13),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 14),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 15),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 16),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 17),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 18),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 19),
    overworld_frame(sGfx_GunkEmoticons, 2, 2, 20),
};

static const union AnimCmd sAnimCmd_ExclamationMark1[] = {
    ANIMCMD_FRAME( 0,  4),
    ANIMCMD_FRAME( 1,  4),
    ANIMCMD_FRAME( 2, 52),
    ANIMCMD_END
};

static const union AnimCmd sAnimCmd_DoubleExclMark[] = {
    ANIMCMD_FRAME( 6,  4),
    ANIMCMD_FRAME( 7,  4),
    ANIMCMD_FRAME( 8, 52),
    ANIMCMD_END
};

static const union AnimCmd sAnimCmd_X[] = {
    ANIMCMD_FRAME( 3,  4),
    ANIMCMD_FRAME( 4,  4),
    ANIMCMD_FRAME( 5, 52),
    ANIMCMD_END
};

static const union AnimCmd sAnimCmd_SmileyFace[] = {
    ANIMCMD_FRAME( 9,  4),
    ANIMCMD_FRAME(10,  4),
    ANIMCMD_FRAME(11, 52),
    ANIMCMD_END
};

static const union AnimCmd sAnimCmd_QuestionMark[] = {
    ANIMCMD_FRAME(12,  4),
    ANIMCMD_FRAME(13,  4),
    ANIMCMD_FRAME(14, 52),
    ANIMCMD_END
};

static const union AnimCmd sAnimCmd_GunkNote[] = {
    ANIMCMD_FRAME(15,  4),
    ANIMCMD_FRAME(16,  4),
    ANIMCMD_FRAME(17, 52),
    ANIMCMD_END
};

static const union AnimCmd sAnimCmd_GunkDots[] = {
    ANIMCMD_FRAME(18,  4),
    ANIMCMD_FRAME(19,  4),
    ANIMCMD_FRAME(20, 52),
    ANIMCMD_END
};

static const union AnimCmd *const sSpriteAnimTable_GunkEmoticons[] = {
    [GUNK_EMOTE_EXCLAMATION] = sAnimCmd_ExclamationMark1,
    [GUNK_EMOTE_DOUBLE_EXCL] = sAnimCmd_DoubleExclMark,
    [GUNK_EMOTE_X]           = sAnimCmd_X,
    [GUNK_EMOTE_SMILE]       = sAnimCmd_SmileyFace,
    [GUNK_EMOTE_QUESTION]    = sAnimCmd_QuestionMark,
    [GUNK_EMOTE_NOTE]        = sAnimCmd_GunkNote,
    [GUNK_EMOTE_DOTS]        = sAnimCmd_GunkDots,
};

static const struct SpriteTemplate sSpriteTemplate_GunkEmoticons = {
    .tileTag = 0xFFFF,
    .paletteTag = 0xFFFF,
    .oam = &sOamData_GunkEmoticons,
    .anims = sSpriteAnimTable_GunkEmoticons,
    .images = sSpriteImages_GunkEmoticons,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCB_TrainerIcons
};

void GunkShowEmote(u8 localId, u8 emote)
{
    u8 spriteId = CreateSpriteAtEnd(&sSpriteTemplate_GunkEmoticons, 0, 0, 0x52);

    if (spriteId == MAX_SPRITES)
        return;
    gFieldEffectArguments[0] = localId;
    gFieldEffectArguments[1] = gSaveBlock1Ptr->location.mapNum;
    gFieldEffectArguments[2] = gSaveBlock1Ptr->location.mapGroup;
    SetIconSpriteData(&gSprites[spriteId], FLDEFF_QUESTION_MARK_ICON, emote);
}
