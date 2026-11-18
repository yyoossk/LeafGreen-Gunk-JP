#include "global.h"
#include "bike.h"
#include "field_player_avatar.h"
#include "metatile_behavior.h"
#include "event_object_movement.h"
#include "fieldmap.h"
#include "field_camera.h"
#include "overworld.h"
#include "constants/map_types.h"
#include "constants/songs.h"
#include "gunk_follower.h"
#include "event_data.h"
#define FLAG_JP_BIKE_GEAR 0x0E3

bool8 CanBikeFaceDirectionOnRail(u8 direction, u8 metatileBehavior);
void BikeTransition_FaceDirection(u8 direction);
u8 GetBikeCollision(u8 direction);
void PlayerOnBikeCollide(u8 direction);
bool8 MetatileBehaviorForbidsBiking(u8);

static bool8 CanBikeSwapWithFollower(u8 direction, u8 collision)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];
    s16 x, y;

    if (collision != COLLISION_OBJECT_EVENT)
        return FALSE;
    x = playerObjEvent->currentCoords.x;
    y = playerObjEvent->currentCoords.y;
    MoveCoords(direction, &x, &y);
    if (MetatileBehaviorForbidsBiking(MapGridGetMetatileBehaviorAt(x, y)))
        return FALSE;
    return CanPlayerSwapWithFollower(direction);
}

void BikeTransition_MoveDirection(u8 direction)
{
    struct ObjectEvent *playerObjEvent;

    playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];
    if (!CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior))
    {
        BikeTransition_FaceDirection(playerObjEvent->movementDirection);
    }
    else
    {
        u8 collision = GetBikeCollision(direction);
        bool8 swap = CanBikeSwapWithFollower(direction, collision);

        if (collision > COLLISION_NONE && collision <= COLLISION_ISOLATED_HORIZONTAL_RAIL && !swap)
        {
            if (collision == COLLISION_LEDGE_JUMP)
                PlayerJumpLedge(direction);
            else if (collision != COLLISION_STOP_SURFING
                  && collision != COLLISION_LEDGE_JUMP
                  && collision != COLLISION_PUSHED_BOULDER
                  && collision != COLLISION_DIRECTIONAL_STAIR_WARP)
                PlayerOnBikeCollide(direction);
        }
        else
        {
            // FRLG+: B switches the bike to a second, Mach Bike gear (FLAG_JP_BIKE_GEAR)
            if (!FlagGet(FLAG_JP_BIKE_GEAR))
            {
                if (collision == COLLISION_COUNT)
                    PlayerWalkFast(direction);
                else if (PlayerIsMovingOnRockStairs(direction))
                    PlayerWalkFast(direction);
                else
                    PlayerRideWaterCurrent(direction);
            }
            else
            {
                if (collision == COLLISION_COUNT)
                    PlayerRideWaterCurrent(direction);
                else if (PlayerIsMovingOnRockStairs(direction))
                    PlayerRideWaterCurrent(direction);
                else
                    PlayerWalkFaster(direction);
            }
            if (swap)
                StartFollowerSwapStep(direction);
        }
    }
}

void BikeTransition_Downhill(u8 v)
{
    u8 collision = GetBikeCollision(DIR_SOUTH);
    bool8 swap = CanBikeSwapWithFollower(DIR_SOUTH, collision);

    if (collision == COLLISION_NONE || swap)
    {
        PlayerWalkFaster(DIR_SOUTH);
        if (swap)
            StartFollowerSwapStep(DIR_SOUTH);
    }
    else if (collision == COLLISION_LEDGE_JUMP)
        PlayerJumpLedge(DIR_SOUTH);
}

void BikeTransition_Uphill(u8 direction)
{
    u8 collision = GetBikeCollision(direction);
    bool8 swap = CanBikeSwapWithFollower(direction, collision);

    if (collision == COLLISION_NONE || swap)
    {
        PlayerWalkNormal(direction);
        if (swap)
            StartFollowerSwapStep(direction);
    }
}
