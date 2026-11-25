#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/songs.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.set SPECIAL_JpSetHelpContext, 0x17D
	.set SPECIAL_JpAnimatePcTurnOff, 0xD7
	.set SPECIAL_JpPcOffHelp, 0x190
	.set JpEventScript_PCDisabled, 0x08193DF2
	.set JpEventScript_PCMainMenu, 0x08193DFC
	.set JpText_BootedUpPC, 0x08192B2A
	.section .rodata
	.align 2

@ メニューの「パソコン」: EventScript_PC without AnimatePcTurnOn (no PC in front of the player)
EventScript_JpMenuPC::
	lockall
	goto_if_set FLAG_SYS_PC_STORAGE_DISABLED, JpEventScript_PCDisabled
	setvar VAR_0x8004, 0x1B
	special JpSetHelpContext
	setvar VAR_0x8004, 0
	playse SE_PC_ON
	msgbox JpText_BootedUpPC
	goto JpEventScript_PCMainMenu
	end

@ replaces the start of EventScript_TurnOffPC (JP 0x08193EAA)
EventScript_JpTurnOffPC::
	setvar VAR_0x8004, 0
	playse SE_PC_OFF
	callnative JpMenuPc_IsFacingPcOn
	goto_if_eq VAR_RESULT, FALSE, EventScript_JpTurnOffPCEnd
	special JpAnimatePcTurnOff
EventScript_JpTurnOffPCEnd:
	special JpPcOffHelp
	releaseall
	end

gJpText_MenuPC::
	.string "パソコン$"
gJpStartMenuDesc_PC::
	.string "ポケモンを　あずけたり　ひきだしたり\n"
	.string "どこでも　パソコンを　つかえる$"
gJpText_MenuFly::
	.string "そらをとぶ$"
gJpText_MenuFlash::
	.string "フラッシュ$"
gJpStartMenuDesc_Fly::
	.string "いったことの　ある　まちへ\n"
	.string "ひとっとびで　とんでいける$"
gJpStartMenuDesc_Flash::
	.string "くらい　ばしょを\n"
	.string "あかるく　てらす$"
