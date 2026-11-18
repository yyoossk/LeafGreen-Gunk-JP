#include "global.h"
#include "gflib.h"
#include "gba/flash_internal.h"
#include "load_save.h"
#include "pokemon.h"
#include "pokemon_storage_system.h"
#include "random.h"
#include "item.h"
#include "save_location.h"
#include "berry_powder.h"
#include "overworld.h"
#include "quest_log.h"
#include "sloopsvc.h"
#include "gunk_follower.h"

void SaveObjectEvents(void);
void SaveSerializedGame(void)
{
    SavePlayerParty();
    SaveObjectEvents();
    ClearFollowerFromSaveBlock();
}
