#include "global.h"
#include "gflib.h"
#include "script.h"
#include "mystery_event_script.h"
#include "event_data.h"
#include "random.h"
#include "item.h"
#include "overworld.h"
#include "field_screen_effect.h"
#include "quest_log.h"
#include "map_preview_screen.h"
#include "fieldmap.h"
#include "field_weather.h"
#include "field_tasks.h"
#include "field_fadetransition.h"
#include "field_player_avatar.h"
#include "script_movement.h"
#include "event_object_movement.h"
#include "event_object_lock.h"
#include "field_message_box.h"
#include "new_menu_helpers.h"
#include "script_menu.h"
#include "data.h"
#include "field_specials.h"
#include "constants/items.h"
#include "script_pokemon_util.h"
#include "pokemon_storage_system.h"
#include "party_menu.h"
#include "money.h"
#include "coins.h"
#include "battle_setup.h"
#include "shop.h"
#include "slot_machine.h"
#include "field_effect.h"
#include "fieldmap.h"
#include "field_door.h"
#include "constants/event_objects.h"
#include "constants/maps.h"
#include "constants/sound.h"
#include "sloopsvc.h"
#include "gunk_follower.h"

extern u16 sMovingNpcId;

bool8 ScrCmd_applymovement(struct ScriptContext * ctx)
{
    u16 localId = VarGet(ScriptReadHalfword(ctx));
    const void *movementScript = (const void *)ScriptReadWord(ctx);

    ScriptMovement_StartObjectMovementScript(localId, gSaveBlock1Ptr->location.mapNum, gSaveBlock1Ptr->location.mapGroup, movementScript);
    Gunk_FollowerOnScriptMovement(localId, movementScript);
    sMovingNpcId = localId;
    return FALSE;
}

bool8 ScrCmd_applymovementat(struct ScriptContext * ctx)
{
    u16 localId = VarGet(ScriptReadHalfword(ctx));
    const void *movementScript = (const void *)ScriptReadWord(ctx);
    u8 mapGroup = ScriptReadByte(ctx);
    u8 mapNum = ScriptReadByte(ctx);

    ScriptMovement_StartObjectMovementScript(localId, mapNum, mapGroup, movementScript);
    Gunk_FollowerOnScriptMovement(localId, movementScript);
    sMovingNpcId = localId;
    return FALSE;
}
