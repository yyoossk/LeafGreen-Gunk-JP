#include "global.h"
#include "gflib.h"
#include "bike.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "fieldmap.h"
#include "field_camera.h"
#include "field_control_avatar.h"
#include "field_effect.h"
#include "field_effect_helpers.h"
#include "field_player_avatar.h"
#include "help_system.h"
#include "metatile_behavior.h"
#include "new_menu_helpers.h"
#include "overworld.h"
#include "party_menu.h"
#include "quest_log.h"
#include "quest_log_player.h"
#include "random.h"
#include "script.h"
#include "strings.h"
#include "wild_encounter.h"
#include "constants/event_object_movement.h"
#include "constants/event_objects.h"
#include "constants/songs.h"
#include "constants/metatile_behaviors.h"
#include "constants/moves.h"
#include "constants/trainer_types.h"
#include "gunk_follower.h"

u8 CheckForPlayerAvatarCollision(u8 direction);
void PlayerNotOnBikeCollide(u8 direction);
extern const u8 sQuestLogSurfDismountActionIds[];
void CreateStopSurfingTask(u8 direction);
void PlayerRunSlow(u8 direction);
void PlayerWalkSlow(u8 direction);
void PlayerSetAnimId(u8 movementActionId, u8 copyableMovement);

void PlayerNotOnBikeMoving(u8 direction, u16 heldKeys)
{
    u8 collision = CheckForPlayerAvatarCollision(direction);
    bool8 swap = (collision == COLLISION_OBJECT_EVENT && CanPlayerSwapWithFollower(direction));

    if (collision != COLLISION_NONE && !swap)
    {
        if (collision == COLLISION_LEDGE_JUMP)
        {
            PlayerJumpLedge(direction);
        }
        else if (collision == COLLISION_DIRECTIONAL_STAIR_WARP)
        {
            PlayerFaceDirection(direction);
        }
        else if (collision != COLLISION_STOP_SURFING
              && collision != COLLISION_LEDGE_JUMP
              && collision != COLLISION_PUSHED_BOULDER
              && collision != COLLISION_DIRECTIONAL_STAIR_WARP)
        {
            PlayerNotOnBikeCollide(direction);
        }
        return;
    }

    if (gPlayerAvatar.flags & PLAYER_AVATAR_FLAG_SURFING)
    {
        // FRLG+ fast surfing: faster only while B is held
        if (heldKeys & B_BUTTON)
            PlayerWalkFaster(direction);
        else
            PlayerWalkFast(direction);
        return;
    }

    // B dash (like the original game): with the Running Shoes, run while B is held
    // (Gunk ran by default and walked with B; changed back at the user's request)
    if ((heldKeys & B_BUTTON) && FlagGet(FLAG_SYS_B_DASH)
        && !IsRunningDisallowed(gObjectEvents[gPlayerAvatar.objectEventId].currentMetatileBehavior))
    {
        if (PlayerIsMovingOnRockStairs(direction))
            PlayerRunSlow(direction);
        else
            PlayerRun(direction);
        gPlayerAvatar.flags |= PLAYER_AVATAR_FLAG_DASH;
    }
    else
    {
        if (PlayerIsMovingOnRockStairs(direction))
            PlayerWalkSlow(direction);
        else
            PlayerWalkNormal(direction);
    }

    if (swap)
        StartFollowerSwapStep(direction);
}

bool8 CanStopSurfing(s16 x, s16 y, u8 direction)
{
    u8 makeWayDirection = DIR_NONE;

    if (!(gPlayerAvatar.flags & PLAYER_AVATAR_FLAG_SURFING) || MapGridGetElevationAt(x, y) != 3)
        return FALSE;
    if (GetObjectEventIdByPosition(x, y, 3) != OBJECT_EVENTS_COUNT)
    {
        makeWayDirection = GetFollowerMakeWayDirection(x, y, direction);
        if (makeWayDirection == DIR_NONE)
            return FALSE;
    }

    QuestLogRecordPlayerAvatarGfxTransitionWithDuration(sQuestLogSurfDismountActionIds[direction], 16);
    CreateStopSurfingTask(direction);
    if (makeWayDirection != DIR_NONE)
        StartFollowerMakeWayStep(makeWayDirection);
    return TRUE;
}

void PlayerJumpLedge(u8 direction)
{
    struct ObjectEvent *playerObj = &gObjectEvents[gPlayerAvatar.objectEventId];
    s16 x = playerObj->currentCoords.x;
    s16 y = playerObj->currentCoords.y;
    u8 makeWayDirection;

    MoveCoords(direction, &x, &y);
    MoveCoords(direction, &x, &y);
    makeWayDirection = GetFollowerMakeWayDirection(x, y, direction);

    PlaySE(SE_LEDGE);
    PlayerSetAnimId(GetJump2MovementAction(direction), 8);
    if (makeWayDirection != DIR_NONE)
        StartFollowerMakeWayStep(makeWayDirection);
}
