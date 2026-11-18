#include "global.h"
#include "daycare.h"
#include "event_data.h"
#include "pokemon.h"
#include "random.h"
#include "constants/daycare.h"
#include "constants/items.h"
#include "constants/flags.h"
#include "constants/species.h"
// FRLG+ (from Emerald): an Everstone holder passes its nature on half the time.
// The egg's whole 32-bit personality is chosen here. FRLG's DayCare keeps only the low half (u16; FRLG+ widened it
// to u32 and so overlapped giftRibbons[0]), so the high half waits in VAR_JP_EGG_PID_HI until SetInitialEggData.
#define VAR_JP_EGG_PID_HI 0x402E

u8 GetNatureFromPersonality(u32 personality);

static s32 GetParentToInheritNature(struct DayCare *daycare)
{
    s32 i;
    s32 dittoCount;
    s32 parent = -1;

    for (i = 0; i < DAYCARE_MON_COUNT; i++)
    {
        if (GetBoxMonGender(&daycare->mons[i].mon) == MON_FEMALE)
            parent = i;
    }
    for (dittoCount = 0, i = 0; i < DAYCARE_MON_COUNT; i++)
    {
        if (GetBoxMonData(&daycare->mons[i].mon, MON_DATA_SPECIES) == SPECIES_DITTO)
            dittoCount++, parent = i;
    }
    if (dittoCount == DAYCARE_MON_COUNT)
        parent = (Random() >= 0xFFFF / 2) ? 0 : 1;
    // FRLG+ fix: a male/genderless pair with no Ditto leaves parent at -1; vanilla Emerald read mons[-1] here
    if (parent < 0)
        return -1;
    if (GetBoxMonData(&daycare->mons[parent].mon, MON_DATA_HELD_ITEM) != ITEM_EVERSTONE || Random() >= 0xFFFF / 2)
        return -1;
    return parent;
}

void _TriggerPendingDaycareEgg(struct DayCare *daycare)
{
    s32 parent = GetParentToInheritNature(daycare);
    u32 personality;

    if (parent < 0)
    {
        personality = ((u32)Random() << 16) | ((Random() % 0xFFFE) + 1);
    }
    else
    {
        u8 wantedNature = GetNatureFromPersonality(GetBoxMonData(&daycare->mons[parent].mon, MON_DATA_PERSONALITY, NULL));
        s32 tries = 0;

        do
        {
            personality = ((u32)Random() << 16) | Random();
            if (wantedNature == GetNatureFromPersonality(personality) && (personality & 0xFFFF) != 0)
                break;
            tries++;
        } while (tries <= 2400);
        if ((personality & 0xFFFF) == 0)   // the low half must stay non-zero: 0 means "no egg"
            personality |= 1;
    }
    daycare->offspringPersonality = personality & 0xFFFF;
    VarSet(VAR_JP_EGG_PID_HI, personality >> 16);
    FlagSet(FLAG_PENDING_DAYCARE_EGG);
}

void _TriggerPendingDaycareMaleEgg(struct DayCare *daycare)
{
    // FRLG+ fix: the upper half is random too (FRLG+ left it zero once SetInitialEggData stopped adding it)
    daycare->offspringPersonality = Random() | EGG_GENDER_MALE;
    VarSet(VAR_JP_EGG_PID_HI, Random());
    FlagSet(FLAG_PENDING_DAYCARE_EGG);
}

// JP SetInitialEggData: called where it called Random() for the personality's upper half
u16 JpEggPidHigh(void)
{
    u16 hi = VarGet(VAR_JP_EGG_PID_HI);

    VarSet(VAR_JP_EGG_PID_HI, 0);
    if (hi == 0)   // an egg made pending before this version
        hi = Random();
    return hi;
}
