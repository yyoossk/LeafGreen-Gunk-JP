#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.section .rodata
	.align 2

@ 赤フルカラー: after the Hall of Fame the Celadon Dept. 2F TM clerk sells every TM except the 5 Game Corner prizes
JpEventScript_CeladonTMClerk::
	goto_if_unset FLAG_SYS_GAME_CLEAR, 0x081834F6
	.byte 0x25, 0x87, 0x01, 0x21, 0x0D, 0x80, 0x02, 0x00, 0x06, 0x01, 0x46, 0x4C, 0x19, 0x08  @ goto_if_questlog EventScript_ReleaseEnd (copied)
	lock
	faceplayer
	message 0x0819372A
	waitmessage
	pokemart JpCeladon_AllTMs
	goto 0x08183511

	.align 2
JpCeladon_AllTMs::
	.2byte 289  @ TM01
	.2byte 290  @ TM02
	.2byte 291  @ TM03
	.2byte 292  @ TM04
	.2byte 293  @ TM05
	.2byte 294  @ TM06
	.2byte 295  @ TM07
	.2byte 296  @ TM08
	.2byte 297  @ TM09
	.2byte 298  @ TM10
	.2byte 299  @ TM11
	.2byte 300  @ TM12
	.2byte 302  @ TM14
	.2byte 303  @ TM15
	.2byte 304  @ TM16
	.2byte 305  @ TM17
	.2byte 306  @ TM18
	.2byte 307  @ TM19
	.2byte 308  @ TM20
	.2byte 309  @ TM21
	.2byte 310  @ TM22
	.2byte 313  @ TM25
	.2byte 314  @ TM26
	.2byte 315  @ TM27
	.2byte 316  @ TM28
	.2byte 318  @ TM30
	.2byte 319  @ TM31
	.2byte 320  @ TM32
	.2byte 321  @ TM33
	.2byte 322  @ TM34
	.2byte 324  @ TM36
	.2byte 325  @ TM37
	.2byte 326  @ TM38
	.2byte 327  @ TM39
	.2byte 328  @ TM40
	.2byte 329  @ TM41
	.2byte 330  @ TM42
	.2byte 331  @ TM43
	.2byte 332  @ TM44
	.2byte 333  @ TM45
	.2byte 334  @ TM46
	.2byte 335  @ TM47
	.2byte 336  @ TM48
	.2byte 337  @ TM49
	.2byte 338  @ TM50
	.2byte 0
