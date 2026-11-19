#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/songs.h"
#include "constants/event_objects.h"
#include "constants/map_scripts.h"
#include "constants/event_object_movement.h"
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
	call EventScript_JpMomGiveShoes
	release
	end

@ 2かいから はじめて おりてきたとき（まだ シューズを もっていない）：おかあさんの よこまで あるいて シューズを もらう
@ プレイヤーのいえ 1かい の ON_FRAME（VAR_TEMP_1 が 0 のとき、マップに はいるたびに 1かいだけ）
EventScript_JpHouse1FFrame::
	lockall
	setvar VAR_TEMP_1, 1
	goto_if_set FLAG_SYS_B_DASH, EventScript_JpHouse1FEnd
	getplayerxy VAR_0x8004, VAR_0x8005
	goto_if_ne VAR_0x8004, 10, EventScript_JpHouse1FEnd
	goto_if_ne VAR_0x8005, 2, EventScript_JpHouse1FEnd
	applymovement OBJ_EVENT_ID_PLAYER, Movement_JpToMom
	waitmovement 0
	applymovement 1, Movement_JpMomFaceRight
	waitmovement 0
	call EventScript_JpMomGiveShoes
EventScript_JpHouse1FEnd:
	releaseall
	end

Movement_JpToMom:
	walk_down
	walk_down
	walk_left
	face_left
	step_end

Movement_JpMomFaceRight:
	face_right
	step_end

EventScript_JpMomGiveShoes:
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
	return

@ プレイヤーのいえ 1かい の マップスクリプト（もとは なにもない）
gJpHouse1FMapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, gJpHouse1FFrameTable
	.byte 0
	.align 2
gJpHouse1FFrameTable::
	map_script_2 VAR_TEMP_1, 0, EventScript_JpHouse1FFrame
	.2byte 0

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
