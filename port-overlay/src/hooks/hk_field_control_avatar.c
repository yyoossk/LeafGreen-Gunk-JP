#include "global.h"
#include "gflib.h"
#include "bike.h"
#include "coord_event_weather.h"
#include "daycare.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "event_scripts.h"
#include "fieldmap.h"
#include "field_control_avatar.h"
#include "field_fadetransition.h"
#include "field_player_avatar.h"
#include "field_poison.h"
#include "field_specials.h"
#include "item_menu.h"
#include "link.h"
#include "wonder_news.h"
#include "metatile_behavior.h"
#include "overworld.h"
#include "renewable_hidden_items.h"
#include "quest_log.h"
#include "safari_zone.h"
#include "script.h"
#include "start_menu.h"
#include "trainer_see.h"
#include "vs_seeker.h"
#include "wild_encounter.h"
#include "constants/songs.h"
#include "constants/event_bg.h"
#include "constants/event_objects.h"
#include "constants/maps.h"
#include "constants/metatile_behaviors.h"
#include "gunk_follower.h"

static bool8 IsTalkableObjectEvent(u8 objectEventId)
{
    if (objectEventId == OBJECT_EVENTS_COUNT)
        return FALSE;
    if (gObjectEvents[objectEventId].localId == LOCALID_PLAYER || gObjectEvents[objectEventId].localId == LOCALID_FOLLOWER)
        return FALSE;
    return TRUE;
}

const u8 *GetInteractedLinkPlayerScript(struct MapPosition *position, u8 metatileBehavior, u8 direction)
{
    u8 objectEventId;
    s32 i;

    if (!MetatileBehavior_IsCounter(MapGridGetMetatileBehaviorAt(position->x, position->y)))
        objectEventId = GetObjectEventIdByPosition(position->x, position->y, position->elevation);
    else
        objectEventId = GetObjectEventIdByPosition(position->x + gDirectionToVectors[direction].x, position->y + gDirectionToVectors[direction].y, position->elevation);

    if (!IsTalkableObjectEvent(objectEventId))
        return NULL;

    for (i = 0; i < MAX_LINK_PLAYERS; i++)
    {
        if (gLinkPlayerObjectEvents[i].active == TRUE && gLinkPlayerObjectEvents[i].objEventId == objectEventId)
            return NULL;
    }

    gSelectedObjectEvent = objectEventId;
    gSpecialVar_LastTalked = gObjectEvents[objectEventId].localId;
    gSpecialVar_Facing = direction;
    return GetObjectEventScriptPointerByObjectEventId(objectEventId);
}

const u8 *GetInteractedObjectEventScript(struct MapPosition *position, u8 metatileBehavior, u8 direction)
{
    u8 objectEventId;
    const u8 *script;

    objectEventId = GetObjectEventIdByPosition(position->x, position->y, position->elevation);
    if (objectEventId != OBJECT_EVENTS_COUNT && gObjectEvents[objectEventId].localId == LOCALID_FOLLOWER)
    {
        gSelectedObjectEvent = objectEventId;
        gSpecialVar_LastTalked = LOCALID_FOLLOWER;
        gSpecialVar_Facing = direction;
        return EventScript_GunkFollowerTalk;
    }
    if (!IsTalkableObjectEvent(objectEventId))
    {
        if (MetatileBehavior_IsCounter(metatileBehavior) != TRUE)
            return NULL;

        objectEventId = GetObjectEventIdByPosition(position->x + gDirectionToVectors[direction].x, position->y + gDirectionToVectors[direction].y, position->elevation);
        if (!IsTalkableObjectEvent(objectEventId))
            return NULL;
    }

    if (InUnionRoom() == TRUE && !ObjectEventCheckHeldMovementStatus(&gObjectEvents[objectEventId]))
        return NULL;

    gSelectedObjectEvent = objectEventId;
    gSpecialVar_LastTalked = gObjectEvents[objectEventId].localId;
    gSpecialVar_Facing = direction;

    script = GetObjectEventScriptPointerByObjectEventId(objectEventId);

    script = GetRamScript(gSpecialVar_LastTalked, script);
    return script;
}
