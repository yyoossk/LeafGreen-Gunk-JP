#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/items.h"
#include "constants/map_scripts.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.set SPECIAL_ShowDiploma, 264
	.section .rodata
	.align 2

@ FRLG+: the GAME FREAK designer gives the しんぴのチケット (Navel Rock) after the Kanto diploma,
@ once the player has the National Pokédex
@ The diploma screen returns to the field with a map reload, so the script after "waitstate" never runs
@ (vanilla only had "release / end" there). Like FRLG+, VAR_TEMP_0 = 2 marks it and the map's ON_FRAME
@ script picks it up after the reload.
EventScript_JpDiploma::
	setvar VAR_TEMP_0, 2
	special ShowDiploma
	waitstate
	end

JpCondo3F_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, JpCondo3F_OnFrame
	.byte 0
JpCondo3F_OnFrame:
	map_script_2 VAR_TEMP_0, 2, EventScript_JpDiplomaAfter
	.2byte 0

EventScript_JpDiplomaAfter:
	setvar VAR_TEMP_0, 0
	lockall
	goto_if_set FLAG_RECEIVED_MYSTIC_TICKET, EventScript_JpDiplomaEnd
	checkitem ITEM_MYSTIC_TICKET, 1
	goto_if_eq VAR_RESULT, TRUE, EventScript_JpDiplomaEnd
	goto_if_unset FLAG_SYS_NATIONAL_DEX, EventScript_JpCantGiveMysticTicket
	msgbox Text_JpGiveMysticTicket
	giveitem ITEM_MYSTIC_TICKET, 1
	goto_if_eq VAR_RESULT, FALSE, EventScript_JpDiplomaEnd
	setflag FLAG_RECEIVED_MYSTIC_TICKET
	setflag FLAG_ENABLE_SHIP_NAVEL_ROCK
	msgbox Text_JpExplainMysticTicket
EventScript_JpDiplomaEnd::
	releaseall
	end

EventScript_JpCantGiveMysticTicket::
	msgbox Text_JpCantGiveMysticTicket
	releaseall
	end

Text_JpGiveMysticTicket::
	.string "ずかんを うめてくれた おれいに\n"
	.string "これを あげよう！$"
Text_JpExplainMysticTicket::
	.string "それは しんぴの チケット！\p"
	.string "クチバの みなとから ふねに のれば\n"
	.string "さいはての ことうへ いけるんだ$"
Text_JpCantGiveMysticTicket::
	.string "じつは ずかんの おれいに\n"
	.string "わたしたい ものが あるんだ\p"
	.string "ぜんこく ずかんに なったら\n"
	.string "また きてくれ！$"
