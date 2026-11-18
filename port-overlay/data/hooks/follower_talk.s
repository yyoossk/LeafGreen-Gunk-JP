#include "constants/global.h"
#include "constants/event_objects.h"
#include "constants/event_object_movement.h"
#include "constants/vars.h"
#include "constants/songs.h"
#include "constants/sound.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.section .rodata
	.align 2
EventScript_GunkFollowerTalk::
	lock
	faceplayer
	callnative Gunk_FollowerTalkPrepare
	switch VAR_RESULT
	case 0, EventScript_GunkFollowerTired
	case 1, EventScript_GunkFollowerWary
	case 2, EventScript_GunkFollowerShy
	case 3, EventScript_GunkFollowerSteady
	case 4, EventScript_GunkFollowerHappy
	applymovement LOCALID_FOLLOWER, Movement_GunkFollowerSmile
	playmoncry VAR_0x8004, CRY_MODE_NORMAL
	waitmovement 0
	waitmoncry
	applymovement LOCALID_FOLLOWER, Movement_GunkFollowerSmile
	waitmovement 0
	msgbox Text_GunkFollowerDevoted
	release
	end

EventScript_GunkFollowerTired::
	setvar VAR_0x8005, 6 @ GUNK_EMOTE_DOTS
	callnative Gunk_FollowerEmote
	playmoncry VAR_0x8004, CRY_MODE_FAINT
	waitmoncry
	delay 20
	msgbox Text_GunkFollowerTired
	release
	end

EventScript_GunkFollowerWary::
	playse SE_PIN
	applymovement LOCALID_FOLLOWER, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox Text_GunkFollowerWary
	release
	end

EventScript_GunkFollowerShy::
	applymovement LOCALID_FOLLOWER, Common_Movement_QuestionMark
	waitmovement 0
	msgbox Text_GunkFollowerShy
	release
	end

EventScript_GunkFollowerSteady::
	setvar VAR_0x8005, 5 @ GUNK_EMOTE_NOTE
	callnative Gunk_FollowerEmote
	playmoncry VAR_0x8004, CRY_MODE_NORMAL
	waitmoncry
	delay 20
	msgbox Text_GunkFollowerSteady
	release
	end

EventScript_GunkFollowerHappy::
	applymovement LOCALID_FOLLOWER, Movement_GunkFollowerSmile
	playmoncry VAR_0x8004, CRY_MODE_NORMAL
	waitmovement 0
	waitmoncry
	msgbox Text_GunkFollowerHappy
	release
	end

Movement_GunkFollowerSmile:
	emote_smile
	step_end
Text_GunkFollowerTired::
	.string "{STR_VAR_1}は つかれている。\n"
	.string "すこし やすませて あげよう。$"

Text_GunkFollowerWary::
	.string "{STR_VAR_1}は すこし\n"
	.string "はなれた ところに いる。\p"
	.string "まだ こころを ゆるして\n"
	.string "いない ようだ。$"

Text_GunkFollowerShy::
	.string "{STR_VAR_1}は こちらを みて\n"
	.string "すぐに めを そらした。$"

Text_GunkFollowerSteady::
	.string "{STR_VAR_1}は すぐ うしろを\n"
	.string "ついて きている。$"

Text_GunkFollowerHappy::
	.string "{STR_VAR_1}は うれしそうに\n"
	.string "ついて きている！$"

Text_GunkFollowerDevoted::
	.string "{STR_VAR_1}は とても\n"
	.string "うれしそうだ！\p"
	.string "どこまでも ついて\n"
	.string "きて くれそうだ！$"
