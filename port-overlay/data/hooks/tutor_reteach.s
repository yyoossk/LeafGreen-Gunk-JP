#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/songs.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.set YES, 1
	.set NO, 0
	.set JpEventScript_ChooseMoveTutorMon, 0x081A9250
	.section .rodata
	.align 2

@ FRLG+: a move tutor who has taught once teaches again for 5000 yen
EventScript_JpReteach_DoubleEdge::
	setvar VAR_0x8005, 4
	buffermovename STR_VAR_1, 38
	goto EventScript_JpTutorReteach

EventScript_JpReteach_ThunderWave::
	setvar VAR_0x8005, 11
	buffermovename STR_VAR_1, 86
	goto EventScript_JpTutorReteach

EventScript_JpReteach_RockSlide::
	setvar VAR_0x8005, 13
	buffermovename STR_VAR_1, 157
	goto EventScript_JpTutorReteach

EventScript_JpReteach_Explosion::
	setvar VAR_0x8005, 12
	buffermovename STR_VAR_1, 153
	goto EventScript_JpTutorReteach

EventScript_JpReteach_MegaPunch::
	setvar VAR_0x8005, 0
	buffermovename STR_VAR_1, 5
	goto EventScript_JpTutorReteach

EventScript_JpReteach_MegaKick::
	setvar VAR_0x8005, 2
	buffermovename STR_VAR_1, 25
	goto EventScript_JpTutorReteach

EventScript_JpReteach_DreamEater::
	setvar VAR_0x8005, 10
	buffermovename STR_VAR_1, 138
	goto EventScript_JpTutorReteach

EventScript_JpReteach_SoftBoiled::
	setvar VAR_0x8005, 9
	buffermovename STR_VAR_1, 135
	goto EventScript_JpTutorReteach

EventScript_JpReteach_Substitute::
	setvar VAR_0x8005, 14
	buffermovename STR_VAR_1, 164
	goto EventScript_JpTutorReteach

EventScript_JpReteach_SwordsDance::
	setvar VAR_0x8005, 1
	buffermovename STR_VAR_1, 14
	goto EventScript_JpTutorReteach

EventScript_JpReteach_SeismicToss::
	setvar VAR_0x8005, 6
	buffermovename STR_VAR_1, 69
	goto EventScript_JpTutorReteach

EventScript_JpReteach_Counter::
	setvar VAR_0x8005, 5
	buffermovename STR_VAR_1, 68
	goto EventScript_JpTutorReteach

EventScript_JpReteach_Metronome::
	setvar VAR_0x8005, 8
	buffermovename STR_VAR_1, 118
	goto EventScript_JpTutorReteach

EventScript_JpReteach_Mimic::
	setvar VAR_0x8005, 7
	buffermovename STR_VAR_1, 102
	goto EventScript_JpTutorReteach

EventScript_JpReteach_BodySlam::
	setvar VAR_0x8005, 3
	buffermovename STR_VAR_1, 34
	goto EventScript_JpTutorReteach

EventScript_JpTutorReteach::
	msgbox Text_JpTutorReteach
	showmoneybox 0, 0
	msgbox Text_JpTutorReteach2, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, EventScript_JpTutorReteachDeclined
	checkmoney 5000
	goto_if_eq VAR_RESULT, FALSE, EventScript_JpTutorReteachNoMoney
	msgbox Text_JpTutorReteachWhichMon
	call JpEventScript_ChooseMoveTutorMon
	goto_if_eq VAR_RESULT, FALSE, EventScript_JpTutorReteachDeclined
	removemoney 5000
	updatemoneybox
	playse SE_SHOP
	msgbox Text_JpTutorReteachTaught
	hidemoneybox
	release
	end

EventScript_JpTutorReteachNoMoney::
	msgbox Text_JpTutorReteachNoMoney
	hidemoneybox
	release
	end

EventScript_JpTutorReteachDeclined::
	msgbox Text_JpTutorReteachDeclined
	hidemoneybox
	release
	end

Text_JpTutorReteach::
	.string "おや また きたのかい？\p"
	.string "{STR_VAR_1}を もういちど\n"
	.string "おしえて あげても いいけど\l"
	.string "こんどは 5000えん もらうよ$"
Text_JpTutorReteach2::
	.string "わざを おしえて ほしいかい？$"
Text_JpTutorReteachWhichMon::
	.string "どの ポケモンに おしえるんだい？$"
Text_JpTutorReteachNoMoney::
	.string "おや おかねが たりないようだね$"
Text_JpTutorReteachDeclined::
	.string "そうかい また いつでも おいで$"
Text_JpTutorReteachTaught::
	.string "まいど！ また いつでも おいで$"
Text_JpTutorOnceFree::
	.string "この わざを ただで おしえて\n"
	.string "もらえるのは いちど だけです\p"
	.string "2かいめ からは おかねが\n"
	.string "かかりますが いいですか？$"
