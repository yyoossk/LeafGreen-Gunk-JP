// pret BUGFIX: AI battle history per battler (vanilla kept one ability / item / move list per side and
// looped 8 moves over half-size arrays). (The double-battle target fix is not needed: only the opponent side runs AI here.)
// The extra per-battler arrays live after the vanilla BattleHistory (its allocation is enlarged to 0x58 in patch_port).
#include "global.h"
#include "battle.h"
#include "battle_ai_script_commands.h"
#include "battle_anim.h"
#include "util.h"
#include "constants/battle_move_effects.h"
#include "pokemon.h"
#include "random.h"
#include "item.h"
#include "constants/battle_ai.h"
#include "constants/abilities.h"
#include "constants/moves.h"
#include "constants/hold_effects.h"
#include "constants/opponents.h"

#define AI_THINKING_STRUCT (gBattleResources->ai)
struct JpAIHist { u16 moves[MAX_BATTLERS_COUNT][MAX_MON_MOVES]; u8 abilities[MAX_BATTLERS_COUNT]; u8 itemEffects[MAX_BATTLERS_COUNT]; };
#define JPH ((struct JpAIHist *)((u8 *)gBattleResources->battleHistory + 0x30))
extern const u8 *sAIScriptPtr;

void RecordLastUsedMoveByTarget(void)
{
    s32 i;

    for (i = 0; i < MAX_MON_MOVES; i++)
    {
        if (JPH->moves[gBattlerTarget][i] == gLastMoves[gBattlerTarget])
            break;

        if (JPH->moves[gBattlerTarget][i] == MOVE_NONE)
        {
            JPH->moves[gBattlerTarget][i] = gLastMoves[gBattlerTarget];
            break;
        }
    }
}

void RecordAbilityBattle(u8 battlerId, u8 abilityId)
{
    JPH->abilities[battlerId] = abilityId;
}

void RecordItemEffectBattle(u8 battlerId, u8 itemEffect)
{
    JPH->itemEffects[battlerId] = itemEffect;
}

void Cmd_get_ability(void)
{
    u8 battlerId;

    if (sAIScriptPtr[1] == AI_USER)
        battlerId = gBattlerAttacker;
    else
        battlerId = gBattlerTarget;

    if (gActiveBattler != battlerId)
    {
        if (JPH->abilities[battlerId] != 0)
        {
            AI_THINKING_STRUCT->funcResult = JPH->abilities[battlerId];
            sAIScriptPtr += 2;
            return;
        }
        // abilities that prevent fleeing.
        if (gBattleMons[battlerId].ability == ABILITY_SHADOW_TAG
        || gBattleMons[battlerId].ability == ABILITY_MAGNET_PULL
        || gBattleMons[battlerId].ability == ABILITY_ARENA_TRAP)
        {
            AI_THINKING_STRUCT->funcResult = gBattleMons[battlerId].ability;
            sAIScriptPtr += 2;
            return;
        }

        if (gSpeciesInfo[gBattleMons[battlerId].species].abilities[0] != ABILITY_NONE)
        {
            if (gSpeciesInfo[gBattleMons[battlerId].species].abilities[1] != ABILITY_NONE)
            {
                // AI has no knowledge of opponent, so it guesses which ability.
                if (Random() % 2)
                    AI_THINKING_STRUCT->funcResult = gSpeciesInfo[gBattleMons[battlerId].species].abilities[0];
                else
                    AI_THINKING_STRUCT->funcResult = gSpeciesInfo[gBattleMons[battlerId].species].abilities[1];
            }
            else
            {
                AI_THINKING_STRUCT->funcResult = gSpeciesInfo[gBattleMons[battlerId].species].abilities[0];
            }
        }
        else
        {
             // AI can't actually reach this part since no pokemon has ability 2 and no ability 1.
            AI_THINKING_STRUCT->funcResult = gSpeciesInfo[gBattleMons[battlerId].species].abilities[1];
        }
    }
    else
    {
        // The AI knows its own ability.
        AI_THINKING_STRUCT->funcResult = gBattleMons[battlerId].ability;
    }

    sAIScriptPtr += 2;
}

void Cmd_if_has_move(void)
{
    s32 i;
    const u16 *movePtr = (u16 *)(sAIScriptPtr + 2);

    switch (sAIScriptPtr[1])
    {
    case AI_USER:
    case AI_USER_PARTNER:
        for (i = 0; i < MAX_MON_MOVES; i++)
        {
            if (gBattleMons[gBattlerAttacker].moves[i] == *movePtr)
                break;
        }
        if (i == MAX_MON_MOVES)
            sAIScriptPtr += 8;
        else
            sAIScriptPtr = T1_READ_PTR(sAIScriptPtr + 4);
        break;
    case AI_TARGET:
    case AI_TARGET_PARTNER:
        for (i = 0; i < MAX_MON_MOVES; i++)
        {
            if (JPH->moves[gBattlerTarget][i] == *movePtr)
                break;
        }
        if (i == MAX_MON_MOVES)
            sAIScriptPtr += 8;
        else
            sAIScriptPtr = T1_READ_PTR(sAIScriptPtr + 4);
        break;
    }
}

void Cmd_if_doesnt_have_move(void)
{
    s32 i;
    const u16 *movePtr = (u16 *)(sAIScriptPtr + 2);

    switch (sAIScriptPtr[1])
    {
    case AI_USER:
    case AI_USER_PARTNER:
        for (i = 0; i < MAX_MON_MOVES; i++)
        {
            if (gBattleMons[gBattlerAttacker].moves[i] == *movePtr)
                break;
        }
        if (i != MAX_MON_MOVES)
            sAIScriptPtr += 8;
        else
            sAIScriptPtr = T1_READ_PTR(sAIScriptPtr + 4);
        break;
    case AI_TARGET:
    case AI_TARGET_PARTNER:
        for (i = 0; i < MAX_MON_MOVES; i++)
        {
            if (JPH->moves[gBattlerTarget][i] == *movePtr)
                break;
        }
        if (i != MAX_MON_MOVES)
            sAIScriptPtr += 8;
        else
            sAIScriptPtr = T1_READ_PTR(sAIScriptPtr + 4);
        break;
    }
}

void Cmd_if_has_move_with_effect(void)
{
    s32 i;

    switch (sAIScriptPtr[1])
    {
    case AI_USER:
    case AI_USER_PARTNER:
        for (i = 0; i < MAX_MON_MOVES; i++)
        {
            if (gBattleMons[gBattlerAttacker].moves[i] != 0 && gBattleMoves[gBattleMons[gBattlerAttacker].moves[i]].effect == sAIScriptPtr[2])
                break;
        }
        if (i != MAX_MON_MOVES)
            sAIScriptPtr = T1_READ_PTR(sAIScriptPtr + 3);
        else
            sAIScriptPtr += 7;
        break;
    case AI_TARGET:
    case AI_TARGET_PARTNER:
/*  3 bugs here:
    1: loops 8 times instead of 4
    2: checks attacker's moves instead of AI's moves
    3: never checks i, so the entire check is useless and there's never a jump
    bugs 1 and 3 were fixed in emerald, bug 2 was not
*/
        for (i = 0; i < MAX_MON_MOVES; i++)
        {
            if (gBattleMoves[JPH->moves[gBattlerTarget][i]].effect == sAIScriptPtr[2])
                break;
        }
        if (i == MAX_MON_MOVES)
            sAIScriptPtr += 7;
        else
            sAIScriptPtr = T1_READ_PTR(sAIScriptPtr + 3);
    }
}

void Cmd_if_doesnt_have_move_with_effect(void)
{
    s32 i;

    switch (sAIScriptPtr[1])
    {
    case AI_USER:
    case AI_USER_PARTNER:
        for (i = 0; i < MAX_MON_MOVES; i++)
        {
            if (gBattleMons[gBattlerAttacker].moves[i] != 0 && gBattleMoves[gBattleMons[gBattlerAttacker].moves[i]].effect == sAIScriptPtr[2])
                break;
        }
        if (i != MAX_MON_MOVES)
            sAIScriptPtr += 7;
        else
            sAIScriptPtr = T1_READ_PTR(sAIScriptPtr + 3);
        break;
    case AI_TARGET:
    case AI_TARGET_PARTNER:
        for (i = 0; i < MAX_MON_MOVES; i++)
        {
            if (JPH->moves[gBattlerTarget][i] && gBattleMoves[JPH->moves[gBattlerTarget][i]].effect == sAIScriptPtr[2])
                break;
        }
        if (i != MAX_MON_MOVES)
            sAIScriptPtr += 7;
        else
            sAIScriptPtr = T1_READ_PTR(sAIScriptPtr + 3);
    }
}

void Cmd_get_hold_effect(void)
{
    u8 battlerId;
    u16 side;

    if (sAIScriptPtr[1] == AI_USER)
        battlerId = gBattlerAttacker;
    else
        battlerId = gBattlerTarget;

    if (gActiveBattler != battlerId)
        AI_THINKING_STRUCT->funcResult = JPH->itemEffects[battlerId];
    else
        AI_THINKING_STRUCT->funcResult = ItemId_GetHoldEffect(gBattleMons[battlerId].item);

    sAIScriptPtr += 2;
}
