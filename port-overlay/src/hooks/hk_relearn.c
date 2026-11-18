#include "global.h"
#include "pokemon.h"
#include "constants/species.h"
#include "constants/moves.h"
#include "constants/pokemon.h"
// FRLG+: the Move Reminder (and Gunk's PC わざおしえ) also offers level-up moves of the Pokémon's
// pre-evolutions, up to its own level. A move its own species learns later than its level stays hidden.
// Baby forms only count for a Pokémon that hatched (met level 0).
// Written fresh for the JP port: FRLG+'s version used a gEvolutionLines table, counted only the
// species' own moves in GetNumberOfRelearnableMoves (so the PC said "no moves" when only pre-evolution
// moves were left) and compacted 20 list entries past the end of what it had filled.

extern const u16 *const gLevelUpLearnsets[];
extern const struct Evolution gEvolutionTable[][EVOS_PER_MON];
#define RELEARN_MAX 24   // the relearner's list holds 25 entries, one of them CANCEL

static bool8 IsBaby(u16 species)
{
    switch (species)
    {
    case SPECIES_PICHU: case SPECIES_CLEFFA: case SPECIES_IGGLYBUFF: case SPECIES_SMOOCHUM:
    case SPECIES_TYROGUE: case SPECIES_ELEKID: case SPECIES_MAGBY: case SPECIES_AZURILL: case SPECIES_WYNAUT:
        return TRUE;
    }
    return FALSE;
}

static u16 FindPreEvolution(u16 species)
{
    u16 s;
    u8 j;

    for (s = 1; s < NUM_SPECIES; s++)
        for (j = 0; j < EVOS_PER_MON; j++)
            if (gEvolutionTable[s][j].method != 0 && gEvolutionTable[s][j].targetSpecies == species)
                return s;
    return SPECIES_NONE;
}

// the level at which species learns move by level-up, or 0xFF
static u8 LearnLevel(u16 species, u16 move)
{
    const u16 *ls = gLevelUpLearnsets[species];
    u8 i;

    for (i = 0; i < MAX_LEVEL_UP_MOVES && ls[i] != LEVEL_UP_END; i++)
        if ((ls[i] & LEVEL_UP_MOVE_ID) == move)
            return ls[i] >> 9;
    return 0xFF;
}

static u8 CollectMoves(struct Pokemon *mon, u16 *moves, u8 max)
{
    u16 species = GetMonData(mon, MON_DATA_SPECIES, NULL);
    u8 level = GetMonData(mon, MON_DATA_LEVEL, NULL);
    bool8 hatched = (GetMonData(mon, MON_DATA_MET_LEVEL, NULL) == 0);
    u16 known[MAX_MON_MOVES];
    u16 line[4];
    u8 numLine = 0, numMoves = 0, i, j, k;
    u16 s;

    for (i = 0; i < MAX_MON_MOVES; i++)
        known[i] = GetMonData(mon, MON_DATA_MOVE1 + i, NULL);
    // the Pokémon's own species first, then its pre-evolutions
    for (s = species; s != SPECIES_NONE && numLine < 4; s = FindPreEvolution(s))
    {
        if (s != species && IsBaby(s) && !hatched)
            break;
        line[numLine++] = s;
    }
    for (k = 0; k < numLine; k++)
    {
        const u16 *ls = gLevelUpLearnsets[line[k]];

        for (i = 0; i < MAX_LEVEL_UP_MOVES && ls[i] != LEVEL_UP_END; i++)
        {
            u16 move = ls[i] & LEVEL_UP_MOVE_ID;

            if ((ls[i] >> 9) > level)
                continue;
            if (k != 0 && LearnLevel(species, move) != 0xFF && LearnLevel(species, move) > level)
                continue;   // its own species learns it later
            for (j = 0; j < MAX_MON_MOVES && known[j] != move; j++)
                ;
            if (j != MAX_MON_MOVES)
                continue;
            for (j = 0; j < numMoves && moves[j] != move; j++)
                ;
            if (j != numMoves)
                continue;
            if (numMoves >= max)
                return numMoves;
            moves[numMoves++] = move;
        }
    }
    return numMoves;
}

u8 GetMoveRelearnerMoves(struct Pokemon *mon, u16 *moves)
{
    return CollectMoves(mon, moves, RELEARN_MAX);
}

u8 GetNumberOfRelearnableMoves(struct Pokemon *mon)
{
    u16 moves[RELEARN_MAX];

    if (GetMonData(mon, MON_DATA_SPECIES_OR_EGG, NULL) == SPECIES_EGG)
        return 0;
    return CollectMoves(mon, moves, RELEARN_MAX);
}
