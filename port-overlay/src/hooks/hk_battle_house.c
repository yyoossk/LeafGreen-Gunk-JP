#include "global.h"
#include "event_data.h"
#include "pokemon.h"
#include "random.h"
#include "string_util.h"
#include "battle.h"
#include "constants/species.h"
#include "constants/items.h"
#include "constants/moves.h"
#include "constants/region_map_sections.h"
// FRLG+ Gym Leader rematches at the Seven Island house (the "Battle House").
// The old woman upstairs hears about a Gym Leader whose Fame Checker page is complete; her SPEAROW takes an
// invitation, and from then on the Leader visits the basement now and then (a step counter). A Leader who
// is visiting is absent from the Gym. Each win makes the Leaders' rematch teams one level stronger (max +12).
//
// The state is FRLG+'s struct BattleHouse; it lives in VAR_JP_BATTLE_HOUSE/+1 (FRLG+ used 0x402A/B, which
// Gunk already uses here).

#define VAR_JP_BATTLE_HOUSE 0x408C
#define JP_FIRST_REMATCH_TRAINER 743
#define NUM_REMATCH_LEADERS 7

struct BattleHouse
{
    u16 spearowState:1;
    u16 told:7;          // bit n: leader n (Brock, Misty, Lt. Surge, Erika, Koga, Sabrina, Blaine)
    u16 boxesMoved:1;
    u16 visitor:7;
    u16 spawnFails:3;
    u16 levelGrowth:5;
    u16 steps:8;
};

enum {
    SET_SPEAROW_STATE,
    SET_TOLD_FAMECHECKER,
    SET_VISITOR_STATE,
    SET_LEVEL_GROWTH,
    CHECK_SPEAROW_STATE,
    CHECK_TOLD_FAMECHECKER,
    CHECK_VISITOR_STATE,
    CHECK_LEVEL_GROWTH,
    SET_BOXES_MOVED,
    CHECK_BOXES_MOVED,
    CHECK_ANY_VISITORS,
    CHECK_ALL_TOLD,
    CREATE_VISITOR_STRING,
    FIND_TELLABLE,      // JP port: VAR_0x8004 = the next leader >= VAR_0x8004 whose Fame Checker page is full and who
                        // hasn't been told about; VAR_RESULT = TRUE if found. Buffers the name in STR_VAR_1.
};

static const u8 sJpLeaderNames[NUM_REMATCH_LEADERS][6] = {
    _("タケシ"), _("カスミ"), _("マチス"), _("エリカ"), _("キョウ"), _("ナツメ"), _("カツラ"),
};
static const u8 sJpLeaderGyms[NUM_REMATCH_LEADERS][7] = {
    _("ニビ"), _("ハナダ"), _("クチバ"), _("タマムシ"), _("セキチク"), _("ヤマブキ"), _("グレン"),
};
static const u8 sJpText_And[] = _("と ");
static const u8 sJpText_Comma[] = _(" ");

static struct BattleHouse *GetBattleHouse(void)
{
    return (struct BattleHouse *)GetVarPointer(VAR_JP_BATTLE_HOUSE);
}

// leader 0-6 -> FAMECHECKER_BROCK (2) ... FAMECHECKER_BLAINE (8)
static bool8 FameCheckerFull(u8 leader)
{
    u16 flags = gSaveBlock1Ptr->fameChecker[2 + leader].flavorTextFlags;
    return (flags & 0x3F) == 0x3F;
}

static u8 CountBits(u8 v)
{
    u8 n = 0;
    while (v)
    {
        n += v & 1;
        v >>= 1;
    }
    return n;
}

void UseBattleHouseVar(void)
{
    struct BattleHouse *bh = GetBattleHouse();
    u8 type = gSpecialVar_0x8003;
    u8 arg = gSpecialVar_0x8004;
    u8 i, total, n;

    switch (type)
    {
    case SET_SPEAROW_STATE:
        bh->spearowState ^= 1;
        break;
    case SET_TOLD_FAMECHECKER:
        if (arg < NUM_REMATCH_LEADERS)
            bh->told |= 1 << arg;
        break;
    case SET_VISITOR_STATE:
        if (arg < NUM_REMATCH_LEADERS)
            bh->visitor ^= 1 << arg;
        break;
    case SET_LEVEL_GROWTH:
        if (bh->levelGrowth < 12)
            bh->levelGrowth++;
        break;
    case CHECK_SPEAROW_STATE:
        gSpecialVar_Result = bh->spearowState;
        break;
    case CHECK_TOLD_FAMECHECKER:
        gSpecialVar_Result = (arg < NUM_REMATCH_LEADERS) ? (bh->told >> arg) & 1 : 0;
        break;
    case CHECK_VISITOR_STATE:
        gSpecialVar_Result = (arg < NUM_REMATCH_LEADERS) ? (bh->visitor >> arg) & 1 : 0;
        break;
    case CHECK_LEVEL_GROWTH:
        gSpecialVar_Result = bh->levelGrowth > 12 ? 12 : bh->levelGrowth;
        break;
    case SET_BOXES_MOVED:
        bh->boxesMoved = 1;
        break;
    case CHECK_BOXES_MOVED:
        gSpecialVar_Result = bh->boxesMoved;
        break;
    case CHECK_ANY_VISITORS:
        gSpecialVar_Result = 0;
        for (i = 0; i < NUM_REMATCH_LEADERS; i++)
        {
            if (bh->visitor & (1 << i))
            {
                gSpecialVar_Result++;
                StringCopy(gStringVar1, sJpLeaderNames[i]);
            }
        }
        ConvertIntToDecimalStringN(gStringVar2, gSpecialVar_Result, STR_CONV_MODE_LEFT_ALIGN, 1);
        break;
    case CHECK_ALL_TOLD:
        gSpecialVar_Result = CountBits(bh->told);
        break;
    case CREATE_VISITOR_STRING:   // 「タケシ、カスミ と マチス」
        total = CountBits(bh->visitor);
        gStringVar1[0] = 0xFF;
        for (i = 0, n = 0; i < NUM_REMATCH_LEADERS; i++)
        {
            if (!(bh->visitor & (1 << i)))
                continue;
            if (n != 0)
                StringAppend(gStringVar1, (n == total - 1) ? sJpText_And : sJpText_Comma);
            StringAppend(gStringVar1, sJpLeaderNames[i]);
            n++;
        }
        gSpecialVar_Result = total;
        break;
    case FIND_TELLABLE:
        gSpecialVar_Result = FALSE;
        for (i = arg; i < NUM_REMATCH_LEADERS; i++)
        {
            if (!(bh->told & (1 << i)) && FameCheckerFull(i))
            {
                gSpecialVar_0x8004 = i;
                StringCopy(gStringVar1, sJpLeaderNames[i]);
                StringCopy(gStringVar3, sJpLeaderGyms[i]);
                gSpecialVar_Result = TRUE;
                break;
            }
        }
        break;
    }
}

// For the Gyms' map scripts: VAR_RESULT = TRUE if leader VAR_0x8004 is visiting Seven Island
void JpBattleHouse_IsLeaderAway(void)
{
    struct BattleHouse *bh = GetBattleHouse();
    gSpecialVar_Result = (bh->visitor >> gSpecialVar_0x8004) & 1;
}

static bool8 AllPossibleGymLeadersPresent(struct BattleHouse *bh)
{
    return (bh->told & ~bh->visitor) == 0;
}

// called for every step the player takes (Gunk's ProcessPlayerFieldInput)
void UpdateBattleHouseStepCounter(void)
{
    struct BattleHouse *bh = GetBattleHouse();
    u8 counter;

    if (VarGet(VAR_JP_BATTLE_HOUSE) == 0 || gMapHeader.regionMapSectionId == MAPSEC_SEVEN_ISLAND)
        return;
    if (bh->steps != 255)
    {
        bh->steps++;
        return;
    }
    bh->steps = 0;
    if (bh->spearowState && !bh->boxesMoved)
    {
        // SPEAROW's first trip: it comes back, the basement opens, and every invited Leader visits
        bh->spearowState = 0;
        bh->boxesMoved = 1;
        bh->visitor |= bh->told;
        return;
    }
    if (bh->spearowState)
    {
        if (Random() % 2 == 0)
            bh->spearowState = 0;
        return;
    }
    if (!AllPossibleGymLeadersPresent(bh) && (bh->spawnFails == 6 || Random() % 256 < 46))
    {
        // a Leader visits (~18%); after 6 misses a visit is forced
        counter = 0;
        do
        {
            u8 leader = Random() % NUM_REMATCH_LEADERS;
            if ((bh->told & (1 << leader)) && !(bh->visitor & (1 << leader)))
            {
                bh->visitor |= 1 << leader;
                bh->spawnFails = 0;
                return;
            }
            counter++;
        } while (counter < 3 || bh->spawnFails >= 6);
        if (bh->spawnFails != 7 && !AllPossibleGymLeadersPresent(bh))
            bh->spawnFails++;
    }
    else if (bh->spawnFails != 7 && !AllPossibleGymLeadersPresent(bh))
    {
        bh->spawnFails++;
    }
}

// ---------------------------------------------------------------- the rematch teams
struct JpRematchMon
{
    u8 iv;
    u8 lvl;
    u16 species;
    u16 heldItem;
    u8 abilityNum;
    u16 moves[4];
};
#include "gen/rematch_parties.h"

static const struct JpRematchMon *const sRematchParties[NUM_REMATCH_LEADERS] = {
    sParty_BrockRematch, sParty_MistyRematch, sParty_LtSurgeRematch, sParty_ErikaRematch,
    sParty_KogaRematch, sParty_SabrinaRematch, sParty_BlaineRematch,
};

// The same teams in the vanilla TrainerMonItemCustomMoves layout, for gTrainers[743-749].party: code that
// reads the party without building it (level sums and the like) sees the right Pokémon.
struct JpTrainerMonItemCustomMoves
{
    u16 iv;
    u8 lvl;
    u16 species;
    u16 heldItem;
    u16 moves[4];
};
#include "gen/rematch_parties_vanilla.h"


u8 JpCreateNPCTrainerParty(struct Pokemon *party, u16 trainerNum);   // the JP original
void ZeroEnemyPartyMons(void);
extern const struct BattleMove gBattleMoves[];

// JP port: replaces the BL to CreateNPCTrainerParty in the battle setup
u8 JpMaster_CreateParty(struct Pokemon *party, u16 trainerNum);
u8 JpCreateNPCTrainerPartyWrapper(struct Pokemon *party, u16 trainerNum)
{
    const struct JpRematchMon *p;
    u8 i, j, level;
    u32 personality;

    if ((i = JpMaster_CreateParty(party, trainerNum)) != 0)
        return i;
    if (trainerNum < JP_FIRST_REMATCH_TRAINER || trainerNum >= JP_FIRST_REMATCH_TRAINER + NUM_REMATCH_LEADERS
     || !(gBattleTypeFlags & BATTLE_TYPE_TRAINER))
        return JpCreateNPCTrainerParty(party, trainerNum);

    p = sRematchParties[trainerNum - JP_FIRST_REMATCH_TRAINER];
    ZeroEnemyPartyMons();
    for (i = 0; i < 6; i++)
    {
        u8 ability = p[i].abilityNum;
        u16 item = p[i].heldItem;

        level = p[i].lvl + (GetBattleHouse()->levelGrowth > 12 ? 12 : GetBattleHouse()->levelGrowth);
        personality = (Random() << 16) | Random();
        CreateMon(&party[i], p[i].species, level, p[i].iv * 31 / 255, TRUE, personality, OT_ID_RANDOM_NO_SHINY, 0);
        SetMonData(&party[i], MON_DATA_HELD_ITEM, &item);
        for (j = 0; j < MAX_MON_MOVES; j++)
        {
            SetMonData(&party[i], MON_DATA_MOVE1 + j, &p[i].moves[j]);
            SetMonData(&party[i], MON_DATA_PP1 + j, &gBattleMoves[p[i].moves[j]].pp);
        }
        if (gSpeciesInfo[p[i].species].abilities[1] != ABILITY_NONE)
            SetMonData(&party[i], MON_DATA_ABILITY_NUM, &ability);
    }
    return 6;
}

// ---------------------------------------------------------------- script helpers
extern const u8 *const gJpLeaderTexts[NUM_REMATCH_LEADERS * 6];
#define JP_SCRIPT_CTX_DATA0 (*(u32 *)(0x03000EB0 + 0x64))   // sGlobalScriptContext.data[0]

// msgbox text for leader VAR_0x8004, kind VAR_0x8006 (followed by callstd in the script)
void JpBH_LoadLeaderText(void)
{
    u16 leader = gSpecialVar_0x8004, kind = gSpecialVar_0x8006;
    if (leader < NUM_REMATCH_LEADERS && kind < 6)
        JP_SCRIPT_CTX_DATA0 = (u32)gJpLeaderTexts[leader * 6 + kind];
}

// basement ON_TRANSITION: a Leader who isn't visiting is hidden (FLAG_TEMP_1 + leader)
void JpBH_HideAbsentLeaders(void)
{
    struct BattleHouse *bh = GetBattleHouse();
    u8 i;
    for (i = 0; i < NUM_REMATCH_LEADERS; i++)
        if (!(bh->visitor & (1 << i)))
            FlagSet(FLAG_TEMP_1 + i);
}

// Gyms' ON_TRANSITION: the Leader VAR_0x8004 is away at Seven Island -> FLAG_TEMP_1F hides the Leader
void JpBH_HideLeaderIfAway(void)
{
    struct BattleHouse *bh = GetBattleHouse();
    if ((bh->visitor >> gSpecialVar_0x8004) & 1)
        FlagSet(FLAG_TEMP_1F);
}
