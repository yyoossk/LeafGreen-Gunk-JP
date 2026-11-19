#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/songs.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.set SPECIAL_JpDisableMsgBoxWalkaway, 0x171
	.set JpEventScript_Mom, 0x0817B855
	.set JpText_ReceivedRunningShoes, 0x08170C20
	.set JpText_SwitchedShoes, 0x08170C36
	.set JpText_ExplainRunningShoes, 0x08170C4C
	.set JpEventScript_RestorePrevTextColor, 0x08193ADB
	.section .rodata
	.align 2

@ ランニングシューズは おかあさんから もらう (ニビの はかせの じょしゅは でてこない)
EventScript_JpMom::
	lock
	faceplayer
	goto_if_set FLAG_SYS_B_DASH, JpEventScript_Mom
	msgbox Text_JpMomRunningShoes
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playfanfare MUS_OBTAIN_KEY_ITEM
	message JpText_ReceivedRunningShoes
	waitmessage
	waitfanfare
	msgbox JpText_SwitchedShoes
	special JpDisableMsgBoxWalkaway
	signmsg
	msgbox JpText_ExplainRunningShoes
	normalmsg
	call JpEventScript_RestorePrevTextColor
	setflag FLAG_SYS_B_DASH
	@ already beat Brock (the aide is waiting in Pewter): send him home
	goto_if_ne VAR_MAP_SCENE_PEWTER_CITY, 1, EventScript_JpMomShoesBye
	setvar VAR_MAP_SCENE_PEWTER_CITY, 2
	setflag FLAG_HIDE_PEWTER_CITY_RUNNING_SHOES_GUY
EventScript_JpMomShoesBye:
	msgbox Text_JpMomShoesBye
	release
	end

@ PewterCity_Gym_EventScript_DefeatedBrock: the aide only comes when the shoes were not received yet
EventScript_JpBrockScene::
	setflag FLAG_HIDE_PEWTER_CITY_GYM_GUIDE
	goto_if_set FLAG_SYS_B_DASH, EventScript_JpBrockSceneShoes
	setvar VAR_MAP_SCENE_PEWTER_CITY, 1
	clearflag FLAG_HIDE_PEWTER_CITY_RUNNING_SHOES_GUY
	return
EventScript_JpBrockSceneShoes:
	setvar VAR_MAP_SCENE_PEWTER_CITY, 2
	return

Text_JpMomRunningShoes::
	.string "おかあさん“{PLAYER}！\n"
	.string "ちょっと まって！\p"
	.string "これを はいて いきなさい！$"

Text_JpMomShoesBye::
	.string "おかあさん“これで どこへでも\n"
	.string "はやく いけるわね！\p"
	.string "きを つけて いってらっしゃい！$"
