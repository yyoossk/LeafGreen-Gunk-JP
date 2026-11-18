#include "constants/field_weather.h"
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
	.set SPECIAL_ChoosePartyMon, 159
	.set SPECIAL_ChooseMonForMoveRelearner, 219
	.set SPECIAL_SelectMoveDeleterMove, 220
	.set SPECIAL_MoveDeleterForgetMove, 221
	.set SPECIAL_BufferMoveDeleterNicknameAndMove, 222
	.set SPECIAL_GetNumMovesSelectedMonHas, 223
	.set SPECIAL_TeachMoveRelearnerMove, 224
	.set SPECIAL_IsSelectedMonEgg, 328
	.set JpEventScript_PCMainMenu, 0x08193DFC
	.set JpEventScript_ChoosePCMenu, 0x08193E0C
	.section .rodata
	.align 2

@ Gunk's PC menu: rows are mapped back to the vanilla choices, plus わざおしえ (data/scripts/pc.inc)
EventScript_GunkPCMenuResult::
	callnative Gunk_TranslatePCMenuResult
	goto_if_eq VAR_RESULT, 5, EventScript_GunkMoveTutor
	goto JpEventScript_ChoosePCMenu
	end

EventScript_GunkMoveTutor::
	playse SE_PC_LOGIN
	msgbox Text_GunkMoveTutorRemember, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, EventScript_GunkMoveTutorChooseMonRemember
	msgbox Text_GunkMoveTutorForget, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, EventScript_GunkMoveTutorChooseMonForget
	goto JpEventScript_PCMainMenu
	end

EventScript_GunkMoveTutorChooseMonRemember::
	msgbox Text_GunkMoveTutorWhichMonRemember
	special ChooseMonForMoveRelearner
	waitstate
	goto_if_ge VAR_0x8004, PARTY_SIZE, JpEventScript_PCMainMenu
	special IsSelectedMonEgg
	goto_if_eq VAR_RESULT, TRUE, EventScript_GunkMoveTutorEggRemember
	goto_if_eq VAR_0x8005, 0, EventScript_GunkMoveTutorNoMoves
	msgbox Text_GunkMoveTutorWhichMoveRemember
	special TeachMoveRelearnerMove
	waitstate
	goto_if_eq VAR_0x8004, 0, EventScript_GunkMoveTutorChooseMonRemember
	goto JpEventScript_PCMainMenu
	end

EventScript_GunkMoveTutorEggRemember::
	msgbox Text_GunkMoveTutorEgg
	goto EventScript_GunkMoveTutorChooseMonRemember
	end

EventScript_GunkMoveTutorNoMoves::
	msgbox Text_GunkMoveTutorNoMoves
	goto EventScript_GunkMoveTutorChooseMonRemember
	end

EventScript_GunkMoveTutorChooseMonForget::
	msgbox Text_GunkMoveTutorWhichMonForget
	special ChoosePartyMon
	waitstate
	goto_if_ge VAR_0x8004, PARTY_SIZE, JpEventScript_PCMainMenu
	special IsSelectedMonEgg
	goto_if_eq VAR_RESULT, TRUE, EventScript_GunkMoveTutorEggForget
	special GetNumMovesSelectedMonHas
	goto_if_eq VAR_RESULT, 1, EventScript_GunkMoveTutorOnlyMove
	msgbox Text_GunkMoveTutorWhichMoveForget
	fadescreen FADE_TO_BLACK
	special SelectMoveDeleterMove
	fadescreen FADE_FROM_BLACK
	goto_if_eq VAR_0x8005, MAX_MON_MOVES, EventScript_GunkMoveTutorChooseMonForget
	special BufferMoveDeleterNicknameAndMove
	msgbox Text_GunkMoveTutorConfirmForget, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, EventScript_GunkMoveTutorChooseMonForget
	special MoveDeleterForgetMove
	playfanfare MUS_MOVE_DELETED
	waitfanfare
	msgbox Text_GunkMoveTutorForgotten
	goto JpEventScript_PCMainMenu
	end

EventScript_GunkMoveTutorEggForget::
	msgbox Text_GunkMoveTutorEgg
	goto EventScript_GunkMoveTutorChooseMonForget
	end

EventScript_GunkMoveTutorOnlyMove::
	special BufferMoveDeleterNicknameAndMove
	msgbox Text_GunkMoveTutorOnlyMove
	goto EventScript_GunkMoveTutorChooseMonForget
	end

Text_GunkMoveTutorRemember::
	.string "ポケモンに むかしの わざを\n"
	.string "おもいださせますか？$"
Text_GunkMoveTutorForget::
	.string "ポケモンに わざを\n"
	.string "わすれさせますか？$"
Text_GunkMoveTutorWhichMonRemember::
	.string "どの ポケモンに\n"
	.string "わざを おもいださせますか？$"
Text_GunkMoveTutorWhichMoveRemember::
	.string "どの わざを おもいださせますか？$"
Text_GunkMoveTutorNoMoves::
	.string "その ポケモンには\n"
	.string "おもいだせる わざが ない！$"
Text_GunkMoveTutorEgg::
	.string "タマゴは わざを おぼえていない！$"
Text_GunkMoveTutorWhichMonForget::
	.string "どの ポケモンに\n"
	.string "わざを わすれさせますか？$"
Text_GunkMoveTutorWhichMoveForget::
	.string "どの わざを わすれさせますか？$"
Text_GunkMoveTutorConfirmForget::
	.string "{STR_VAR_1}は\n"
	.string "{STR_VAR_2}を わすれますか？$"
Text_GunkMoveTutorForgotten::
	.string "{STR_VAR_1}は\n"
	.string "{STR_VAR_2}を きれいに わすれた！$"
Text_GunkMoveTutorOnlyMove::
	.string "{STR_VAR_1}は わざを ひとつしか\n"
	.string "しらないので わすれられない！$"
