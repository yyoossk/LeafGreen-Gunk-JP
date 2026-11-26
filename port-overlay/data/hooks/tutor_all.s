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

@ 殿堂入りの あとの「わざおしえ マスター」（タマムシデパート 2かい、FLAG_JP_HIDE_MASTERS が きえると でてくる）
@ おしえわざを ぜんぶ、なんどでも ただで おしえる
EventScript_JpTutorAll::
	lock
	faceplayer
	msgbox Text_JpTutorAllHello
	setvar VAR_RESULT, 0
EventScript_JpTutorAllMenu::
	message Text_JpTutorAllWhich
	waitmessage
	callnative JpTutorAll_Menu
	waitstate
	goto_if_eq VAR_RESULT, 0xFF, EventScript_JpTutorAllBye
	copyvar VAR_0x8005, VAR_RESULT
	callnative JpTutorAll_BufferMove
	msgbox Text_JpTutorAllWhichMon
	call JpEventScript_ChooseMoveTutorMon
	goto_if_eq VAR_RESULT, FALSE, EventScript_JpTutorAllAgain
	msgbox Text_JpTutorAllTaught
EventScript_JpTutorAllAgain::
	setvar VAR_RESULT, 0xFFFE      @ つぎも おなじ ところに カーソル
	goto EventScript_JpTutorAllMenu

EventScript_JpTutorAllBye::
	msgbox Text_JpTutorAllBye
	release
	end

Text_JpTutorAllHello::
	.string "わしは わざおしえ マスター！\p"
	.string "カントーと ナナシマの\n"
	.string "わざおしえの わざを ぜんぶ\l"
	.string "なんどでも ただで おしえて やろう！$"
Text_JpTutorAllWhich::
	.string "どの わざを おしえて ほしい？$"
Text_JpTutorAllWhichMon::
	.string "{STR_VAR_1}を どの ポケモンに\n"
	.string "おしえるんじゃ？$"
Text_JpTutorAllTaught::
	.string "ほかにも おしえて ほしい\n"
	.string "わざは あるかの？$"
Text_JpTutorAllBye::
	.string "また いつでも おいで！$"
