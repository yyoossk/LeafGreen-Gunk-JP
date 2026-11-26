#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/event_objects.h"
#include "constants/event_object_movement.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.set FLAG_JP_FAST_HEAL, 0x4AB              @ せってい「かいふく アニメ」みない
	.set SPECIAL_HealPlayerParty, 0
	.set FLDEFF_POKECENTER_HEAL, 25
	.set JpMovement_NurseFaceLeft, 0x08194729   @ Common_Movement_WalkInPlaceFasterLeft
	.set JpMovement_NurseFaceDown, 0x0819472F   @ Common_Movement_WalkInPlaceFasterDown
	.set JpText_WeHopeToSeeYouAgain, 0x08192E49
	.section .rodata
	.align 2

@ ポケモンセンターの かいふく（EventScript_PkmnCenterNurse_TakeAndHealPkmn 0x08193A34 から goto）
@ せっていで「かいふく アニメ」を みない に すると、かいふくマシンの アニメと きょくを とばす
EventScript_JpNurseHeal::
	goto_if_set FLAG_JP_FAST_HEAL, EventScript_JpNurseHealFast
	applymovement VAR_LAST_TALKED, JpMovement_NurseFaceLeft
	waitmovement 0
	dofieldeffect FLDEFF_POKECENTER_HEAL
	waitfieldeffect FLDEFF_POKECENTER_HEAL
	applymovement VAR_LAST_TALKED, JpMovement_NurseFaceDown
	waitmovement 0
	special HealPlayerParty
	return

EventScript_JpNurseHealFast::
	special HealPlayerParty
	return

@ かいふくの あと「また どうぞ」の あとで しゅじんこうを したに むける
@ （A ボタンを れんだ しても もういちど じょうさんに はなしかけない ように）
EventScript_JpNurseBye::
	msgbox JpText_WeHopeToSeeYouAgain
	applymovement OBJ_EVENT_ID_PLAYER, Movement_JpNursePlayerFaceDown
	waitmovement 0
	callnative JpNurseNoFollowerTalk
	return

Movement_JpNursePlayerFaceDown:
	face_down
	step_end
