#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.set JpEventScript_BufferItemsPocket, 0x08193B5D
	.set JpEventScript_BufferKeyItemsPocket, 0x08193B6D
	.set JpEventScript_BufferPokeBallsPocket, 0x08193B7D
	.set JpEventScript_BufferTMCase, 0x08193B8D
	.set JpEventScript_BufferBerryPouch, 0x08193B9D
	.set JpEventScript_PlayFanfareObtainedItem, 0x08193BC8
	.section .rodata
	.align 2

@ EventScript_BufferPocketNameTryFanfare (0x08193B20) は ポケット 1〜5 しか みないので、
@ くすり(12)・もちもの(13) ポケットの どうぐは ひろえず もらえなかった（スクリプトが とちゅうで おわる）。
@ さいしょの copyvar を ここへの goto に かえる。
EventScript_JpBufferPocketName::
	copyvar VAR_0x8000, VAR_RESULT
	goto_if_eq VAR_0x8000, 1, JpEventScript_BufferItemsPocket
	goto_if_eq VAR_0x8000, 2, JpEventScript_BufferKeyItemsPocket
	goto_if_eq VAR_0x8000, 3, JpEventScript_BufferPokeBallsPocket
	goto_if_eq VAR_0x8000, 4, JpEventScript_BufferTMCase
	goto_if_eq VAR_0x8000, 5, JpEventScript_BufferBerryPouch
	goto_if_eq VAR_0x8000, 12, EventScript_JpBufferMedicinePocket
	goto_if_eq VAR_0x8000, 13, EventScript_JpBufferHeldItemsPocket
	end

EventScript_JpBufferMedicinePocket:
	bufferstring STR_VAR_3, Text_JpMedicinePocket
	call_if_eq VAR_0x8007, TRUE, JpEventScript_PlayFanfareObtainedItem
	return

EventScript_JpBufferHeldItemsPocket:
	bufferstring STR_VAR_3, Text_JpHeldItemsPocket
	call_if_eq VAR_0x8007, TRUE, JpEventScript_PlayFanfareObtainedItem
	return

Text_JpMedicinePocket:
	.string "くすりポケット$"
Text_JpHeldItemsPocket:
	.string "もちものポケット$"
