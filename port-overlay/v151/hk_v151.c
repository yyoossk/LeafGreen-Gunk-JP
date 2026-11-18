// 151匹揃う版: wild encounters use the LeafGreen table half of the time.
// gWildMonHeaders is relocated to [FireRed 132][LeafGreen 132][terminator] by tools/v151_patch.py,
// so index i + JP_NUM_WILD_HEADERS is the LeafGreen table of the same map.
#include "global.h"
#include "event_data.h"
#include "random.h"
#include "wild_encounter.h"
#include "constants/maps.h"

#define JP_NUM_WILD_HEADERS 132
#define HEADER_NONE 0xFFFF
bool8 UnlockedTanobyOrAreNotInTanoby(void);
// called through pointers: this code sits far from everything else (0x08F80000), and plain bl calls would make the
// linker add veneers that shift the shared code
__attribute__((section(".v151data"))) static bool8 (*const sUnlockedTanoby)(void) = UnlockedTanobyOrAreNotInTanoby;
__attribute__((section(".v151data"))) static u16 (*const sRandom)(void) = Random;
__attribute__((section(".v151data"))) static u16 (*const sVarGet)(u16) = VarGet;

__attribute__((section(".v151text"))) u16 GetCurrentMapWildMonHeaderId(void)
{
    u16 i;

    for (i = 0; i < JP_NUM_WILD_HEADERS; i++)
    {
        const struct WildPokemonHeader * wildHeader = &gWildMonHeaders[i];
        if (wildHeader->mapGroup == MAP_GROUP(MAP_UNDEFINED))
            break;

        if (gWildMonHeaders[i].mapGroup == gSaveBlock1Ptr->location.mapGroup &&
            gWildMonHeaders[i].mapNum == gSaveBlock1Ptr->location.mapNum)
        {
            if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_SIX_ISLAND_ALTERING_CAVE) &&
                gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SIX_ISLAND_ALTERING_CAVE))
            {
                u16 alteringCaveId = sVarGet(VAR_ALTERING_CAVE_WILD_SET);
                if (alteringCaveId >= NUM_ALTERING_CAVE_TABLES)
                    alteringCaveId = 0;

                i += alteringCaveId;
            }

            if (!sUnlockedTanoby())
                break;
            if (sRandom() & 1)
                i += JP_NUM_WILD_HEADERS;
            return i;
        }
    }

    return HEADER_NONE;
}
