#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/songs.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set YES, 1
	.set NO, 0
	.set FALSE, 0
	.set TRUE, 1
	.set SPECIAL_SelectMoveDeleterMove, 220
	.set SPECIAL_MoveDeleterForgetMove, 221
	.set SPECIAL_BufferMoveDeleterNicknameAndMove, 222
	.section .rodata
	.align 2

@ 赤フルカラー: party menu "わすれさせる" (HMs too). VAR_0x8004 = party slot, VAR_0x8005 = move slot (4 = cancel)
JpEventScript_PartyForgetMove::
	lockall
	goto_if_eq VAR_0x8005, MAX_MON_MOVES, JpEventScript_PartyForgetMove_End
	special BufferMoveDeleterNicknameAndMove
	msgbox JpText_PartyForget_Confirm, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, JpEventScript_PartyForgetMove_End
	special MoveDeleterForgetMove
	playfanfare MUS_MOVE_DELETED
	waitfanfare
	msgbox JpText_PartyForget_Done
JpEventScript_PartyForgetMove_End:
	releaseall
	end

JpText_PartyForget_Confirm:
	.string "{STR_VAR_1}の\n{STR_VAR_2}を わすれさせますか？$"

JpText_PartyForget_Done:
	.string "{STR_VAR_1}は {STR_VAR_2}の\nつかいかたを きれいに わすれた！$"
