// pret BUGFIX ports (functions replaced whole; the rest of the BUGFIX list is patched in tools/patch_port.py)
#include "global.h"
#include "gflib.h"
#include "battle.h"
#include "battle_anim.h"
#include "event_data.h"
#include "heal_location.h"
#include "link.h"
#include "pokemon.h"
#include "pokedex.h"
#include "pokeball.h"
#include "random.h"
#include "overworld.h"
#include "constants/heal_locations.h"
#include "constants/maps.h"
#include "constants/trade.h"
#include "constants/species.h"

// dodrio_berry_picking: the per-player sprite id buffers were never freed
extern u16 *sDodrioSpriteIds[MAX_RFU_PLAYERS];
void FreeDodrioSprites(u8 numPlayers)
{
    u8 i;
    for (i = 0; i < numPlayers; i++)
    {
        struct Sprite *sprite = &gSprites[*sDodrioSpriteIds[i]];
        if (sprite)
            DestroySpriteAndFreeResources(sprite);
        FREE_AND_SET_NULL(sDodrioSpriteIds[i]);
    }
}

// pokemon: MON_DATA_IVS only read one byte, so CreateMonWithIVsPersonality (roamers) lost most IVs
void CreateMonWithIVsPersonality(struct Pokemon *mon, u16 species, u8 level, u32 ivs, u32 personality)
{
    u8 iv;
    CreateMon(mon, species, level, 0, TRUE, personality, OT_ID_PLAYER_ID, 0);
    iv = ivs & MAX_IV_MASK;         SetMonData(mon, MON_DATA_HP_IV, &iv);
    iv = (ivs >> 5) & MAX_IV_MASK;  SetMonData(mon, MON_DATA_ATK_IV, &iv);
    iv = (ivs >> 10) & MAX_IV_MASK; SetMonData(mon, MON_DATA_DEF_IV, &iv);
    iv = (ivs >> 15) & MAX_IV_MASK; SetMonData(mon, MON_DATA_SPEED_IV, &iv);
    iv = (ivs >> 20) & MAX_IV_MASK; SetMonData(mon, MON_DATA_SPATK_IV, &iv);
    iv = (ivs >> 25) & MAX_IV_MASK; SetMonData(mon, MON_DATA_SPDEF_IV, &iv);
    CalculateMonStats(mon);
}

// trade: Eggs could be traded before the National Dex
u32 CanTradeSelectedMon(struct Pokemon * playerParty, int partyCount, int monIdx)
{
    int i, numMonsLeft;
    struct LinkPlayer * partner;
    int species[PARTY_SIZE];
    int species2[PARTY_SIZE];

    for (i = 0; i < partyCount; i++)
    {
        species2[i] = GetMonData(&playerParty[i], MON_DATA_SPECIES_OR_EGG);
        species[i] = GetMonData(&playerParty[i], MON_DATA_SPECIES);
    }

    // Cant trade Eggs or non-Kanto mons if player doesn't have National Dex
    if (!IsNationalPokedexEnabled())
    {
        // See comment below
        if (species2[monIdx] == SPECIES_EGG)
            return CANT_TRADE_EGG_YET;

        if (species2[monIdx] > KANTO_SPECIES_END)
            return CANT_TRADE_NATIONAL;

        // This is meant to be SPECIES_EGG. There are obviously no circumstances
        // where you're allowed to trade SPECIES_NONE, so it wouldn't make sense to
        // only check this if the National Dex is missing. SPECIES_EGG will accidentally
        // be handled instead by the conditional above. Both of these problems are fixed in Emerald.
    }

    partner = &gLinkPlayers[GetMultiplayerId() ^ 1];
    if ((partner->version & 0xFF) != VERSION_RUBY &&
        (partner->version & 0xFF) != VERSION_SAPPHIRE)
    {
        // Does partner not have National Dex
        if (!(partner->progressFlagsCopy & 0xF))
        {
            if (species2[monIdx] == SPECIES_EGG)
                return CANT_TRADE_PARTNER_EGG_YET;

            if (species2[monIdx] > KANTO_SPECIES_END)
                return CANT_TRADE_INVALID_MON;
        }
    }

    if (species[monIdx] == SPECIES_DEOXYS || species[monIdx] == SPECIES_MEW)
    {
        if (!GetMonData(&playerParty[monIdx], MON_DATA_MODERN_FATEFUL_ENCOUNTER))
            return CANT_TRADE_INVALID_MON;
    }

    // Make Eggs not count for numMonsLeft
    for (i = 0; i < partyCount; i++)
    {
        if (species2[i] == SPECIES_EGG)
            species2[i] = SPECIES_NONE;
    }

    // Count alive mons in party, excluding selected trade mon
    for (numMonsLeft = 0, i = 0; i < partyCount; i++)
    {
        if (i != monIdx)
            numMonsLeft += species2[i];
    }

    if (numMonsLeft != 0)
        return CAN_TRADE_MON;
    else
        return CANT_TRADE_LAST_MON;
}

// pokemon: u16 overflow for high stats
extern const s8 sNatureStatTable[][NUM_NATURE_STATS];
u16 ModifyStatByNature(u8 nature, u16 stat, u8 statIndex)
{
// Because this is a u16 it will be unable to store the
// result of the multiplication for any stat > 595 for a
// positive nature and > 728 for a negative nature.
// Neither occur in the base game, but this can happen if
// any Nature-affected base stat is increased to a value
// above 248. The closest by default is Shuckle at 230.
    u32 retVal;

    // Don't modify HP, Accuracy, or Evasion by nature
    if (statIndex <= STAT_HP || statIndex > NUM_NATURE_STATS)
        return stat;

    switch (sNatureStatTable[nature][statIndex - 1])
    {
    case 1:
        retVal = stat * 110;
        retVal /= 100;
        break;
    case -1:
        retVal = stat * 90;
        retVal /= 100;
        break;
    default:
        retVal = stat;
        break;
    }

    return retVal;
}

// heal_location: out-of-bounds read when no heal location matched
extern const u16 sWhiteoutRespawnHealCenterMapIdxs[][2];
void SetWhiteoutRespawnHealerNpcAsLastTalked(u32 healLocationIdx);
u32 GetHealLocationIndexFromMapGroupAndNum(u16 mapGroup, u16 mapNum);
void SetWhiteoutRespawnWarpAndHealerNpc(struct WarpData * warp)
{
    u32 healLocationIdx;

    if (VarGet(VAR_MAP_SCENE_TRAINER_TOWER) == 1)
    {
        if (!gSaveBlock1Ptr->trainerTower[gSaveBlock1Ptr->towerChallengeId].spokeToOwner)
            VarSet(VAR_MAP_SCENE_TRAINER_TOWER, 0);
        gSpecialVar_LastTalked = 1;
        warp->x = 4;
        warp->y = 11;
        warp->mapGroup = MAP_GROUP(MAP_TRAINER_TOWER_LOBBY);
        warp->mapNum = MAP_NUM(MAP_TRAINER_TOWER_LOBBY);
        warp->warpId = 0xFF;
    }
    else
    {
        healLocationIdx = GetHealLocationIndexFromMapGroupAndNum(gSaveBlock1Ptr->lastHealLocation.mapGroup, gSaveBlock1Ptr->lastHealLocation.mapNum);
        // Avoid out of bounds read
        if (healLocationIdx == HEAL_LOCATION_NONE)
            return;
        warp->mapGroup = sWhiteoutRespawnHealCenterMapIdxs[healLocationIdx - 1][0];
        warp->mapNum = sWhiteoutRespawnHealCenterMapIdxs[healLocationIdx - 1][1];
        warp->warpId = WARP_ID_NONE;

        if (sWhiteoutRespawnHealCenterMapIdxs[healLocationIdx - 1][0] == MAP_GROUP(MAP_PALLET_TOWN_PLAYERS_HOUSE_1F) && sWhiteoutRespawnHealCenterMapIdxs[healLocationIdx - 1][1] == MAP_NUM(MAP_PALLET_TOWN_PLAYERS_HOUSE_1F))
        {
            warp->x = 8;
            warp->y = 5;
        }
        else if (sWhiteoutRespawnHealCenterMapIdxs[healLocationIdx - 1][0] == MAP_GROUP(MAP_INDIGO_PLATEAU_POKEMON_CENTER_1F) && sWhiteoutRespawnHealCenterMapIdxs[healLocationIdx - 1][1] == MAP_NUM(MAP_INDIGO_PLATEAU_POKEMON_CENTER_1F))
        {
            warp->x = 13;
            warp->y = 12;
        }
        else if (sWhiteoutRespawnHealCenterMapIdxs[healLocationIdx - 1][0] == MAP_GROUP(MAP_ONE_ISLAND_POKEMON_CENTER_1F) && sWhiteoutRespawnHealCenterMapIdxs[healLocationIdx - 1][1] == MAP_NUM(MAP_ONE_ISLAND_POKEMON_CENTER_1F))
        {
            warp->x = 5;
            warp->y = 4;
        }
        else if (sWhiteoutRespawnHealCenterMapIdxs[healLocationIdx - 1][0] == MAP_GROUP(MAP_TRAINER_TOWER_LOBBY) && sWhiteoutRespawnHealCenterMapIdxs[healLocationIdx - 1][1] == MAP_NUM(MAP_TRAINER_TOWER_LOBBY))
        {
            warp->x = 4;
            warp->y = 11;
            VarSet(VAR_MAP_SCENE_TRAINER_TOWER, 0);
        }
        else
        {
            warp->x = 7;
            warp->y = 4;
        }
        SetWhiteoutRespawnHealerNpcAsLastTalked(healLocationIdx);
    }
}

// roamer: status was read as u32 (status + contest stats)
#define ROAMER (&gSaveBlock1Ptr->roamer)
void CreateRoamerMonInstance(void)
{
    u32 status;
    struct Pokemon *mon = &gEnemyParty[0];
    ZeroEnemyPartyMons();
    CreateMonWithIVsPersonality(mon, ROAMER->species, ROAMER->level, ROAMER->ivs, ROAMER->personality);
// The roamer's status field is u8, but SetMonData expects status to be u32, so will set the roamer's status
// using the status field and the following 3 bytes (cool, beauty, and cute).
    status = ROAMER->status;
    SetMonData(mon, MON_DATA_STATUS, &status);
    SetMonData(mon, MON_DATA_HP, &ROAMER->hp);
    SetMonData(mon, MON_DATA_COOL, &ROAMER->cool);
    SetMonData(mon, MON_DATA_BEAUTY, &ROAMER->beauty);
    SetMonData(mon, MON_DATA_CUTE, &ROAMER->cute);
    SetMonData(mon, MON_DATA_SMART, &ROAMER->smart);
    SetMonData(mon, MON_DATA_TOUGH, &ROAMER->tough);
}

// pokeball: shrink anim did not play when the affine anim was paused
#define sMonSpriteId data[0]
#define sDelay       data[1]
#define sMonPalNum   data[2]
#define sFadePalsLo  data[3]
#define sFadePalsHi  data[4]
void SpriteCB_TradePokeballSendOff(struct Sprite *sprite);
void AnimateBallOpenParticlesForPokeball(u8 x, u8 y, u8 kindOfStars, u8 subpriority);
u8 LaunchBallFadeMonTaskForPokeball(bool8 unFadeLater, u8 battlerId, u32 arg2);
void SpriteCB_TradePokeball(struct Sprite *sprite)
{
    if (sprite->sDelay == 0)
    {
        u8 subpriority;
        u8 monSpriteId = sprite->sMonSpriteId;
        u8 monPalNum = sprite->sMonPalNum;
        u32 selectedPalettes = (u16)sprite->sFadePalsLo | ((u16)sprite->sFadePalsHi << 16);

        if (sprite->subpriority != 0)
            subpriority = sprite->subpriority - 1;
        else
            subpriority = 0;

        StartSpriteAnim(sprite, 1);
        AnimateBallOpenParticlesForPokeball(sprite->x, sprite->y - 5, sprite->oam.priority, subpriority);
        // sDelay re-used to store task id but never read
        sprite->sDelay = LaunchBallFadeMonTaskForPokeball(TRUE, monPalNum, selectedPalettes);
        sprite->callback = SpriteCB_TradePokeballSendOff;
        // FIX: If this is used on a sprite that has previously had an affine animation, it will not
        // play the shrink anim properly due to being paused.
        gSprites[monSpriteId].affineAnimPaused = FALSE;
        StartSpriteAffineAnim(&gSprites[monSpriteId], BATTLER_AFFINE_RETURN);
        AnimateSprite(&gSprites[monSpriteId]);
        gSprites[monSpriteId].data[1] = 0;
    }
    else
    {
        sprite->sDelay--;
    }
}


// pokemon: current HP could drop to 0 or below when max HP shrank
u8 GetLevelFromMonExp(struct Pokemon *mon);
#define CALC_STAT(base, iv, ev, statIndex, field)               \
{                                                               \
    u8 baseStat = gSpeciesInfo[species].base;                   \
    s32 n = (((2 * baseStat + iv + ev / 4) * level) / 100) + 5; \
    u8 nature = GetNature(mon);                                 \
    n = ModifyStatByNature(nature, n, statIndex);               \
    SetMonData(mon, field, &n);                                 \
}

void CalculateMonStats(struct Pokemon *mon)
{
    s32 oldMaxHP = GetMonData(mon, MON_DATA_MAX_HP, NULL);
    s32 currentHP = GetMonData(mon, MON_DATA_HP, NULL);
    s32 hpIV = GetMonData(mon, MON_DATA_HP_IV, NULL);
    s32 hpEV = GetMonData(mon, MON_DATA_HP_EV, NULL);
    s32 attackIV = GetMonData(mon, MON_DATA_ATK_IV, NULL);
    s32 attackEV = GetMonData(mon, MON_DATA_ATK_EV, NULL);
    s32 defenseIV = GetMonData(mon, MON_DATA_DEF_IV, NULL);
    s32 defenseEV = GetMonData(mon, MON_DATA_DEF_EV, NULL);
    s32 speedIV = GetMonData(mon, MON_DATA_SPEED_IV, NULL);
    s32 speedEV = GetMonData(mon, MON_DATA_SPEED_EV, NULL);
    s32 spAttackIV = GetMonData(mon, MON_DATA_SPATK_IV, NULL);
    s32 spAttackEV = GetMonData(mon, MON_DATA_SPATK_EV, NULL);
    s32 spDefenseIV = GetMonData(mon, MON_DATA_SPDEF_IV, NULL);
    s32 spDefenseEV = GetMonData(mon, MON_DATA_SPDEF_EV, NULL);
    u16 species = GetMonData(mon, MON_DATA_SPECIES, NULL);
    s32 level = GetLevelFromMonExp(mon);
    s32 newMaxHP;

    SetMonData(mon, MON_DATA_LEVEL, &level);

    if (species == SPECIES_SHEDINJA)
    {
        newMaxHP = 1;
    }
    else
    {
        s32 n = 2 * gSpeciesInfo[species].baseHP + hpIV;
        newMaxHP = (((n + hpEV / 4) * level) / 100) + level + 10;
    }

    gBattleScripting.levelUpHP = newMaxHP - oldMaxHP;
    if (gBattleScripting.levelUpHP == 0)
        gBattleScripting.levelUpHP = 1;

    SetMonData(mon, MON_DATA_MAX_HP, &newMaxHP);

    CALC_STAT(baseAttack, attackIV, attackEV, STAT_ATK, MON_DATA_ATK)
    CALC_STAT(baseDefense, defenseIV, defenseEV, STAT_DEF, MON_DATA_DEF)
    CALC_STAT(baseSpeed, speedIV, speedEV, STAT_SPEED, MON_DATA_SPEED)
    CALC_STAT(baseSpAttack, spAttackIV, spAttackEV, STAT_SPATK, MON_DATA_SPATK)
    CALC_STAT(baseSpDefense, spDefenseIV, spDefenseEV, STAT_SPDEF, MON_DATA_SPDEF)

    if (species == SPECIES_SHEDINJA)
    {
        if (currentHP != 0 || oldMaxHP == 0)
            currentHP = 1;
        else
            return;
    }
    else
    {
        if (currentHP == 0 && oldMaxHP == 0)
            currentHP = newMaxHP;
        else if (currentHP != 0) {
            // BUG: currentHP is unintentionally able to become <= 0 after the instruction below.
            currentHP += newMaxHP - oldMaxHP;
            if (currentHP <= 0)
                currentHP = 1;
        }
        else
            return;
    }

    SetMonData(mon, MON_DATA_HP, &currentHP);
}

