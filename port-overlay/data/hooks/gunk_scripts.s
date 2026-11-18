#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/songs.h"
#include "constants/items.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.section .rodata
	.align 2

@ Gunk's repel prompt (data/scripts/repel.inc), Japanese text
EventScript_GunkRepelWoreOff::
	goto_if_set FLAG_GUNK_ENDLESS_REPEL_ON, EventScript_GunkRepelWoreOffMessage
	checkitem VAR_GUNK_LAST_REPEL, 1
	goto_if_eq VAR_RESULT, FALSE, EventScript_GunkRepelWoreOffMessage
	lockall
	bufferitemname STR_VAR_1, VAR_GUNK_LAST_REPEL
	msgbox Text_GunkRepelWoreOffUseAnother, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, EventScript_GunkRepelWoreOffDone
	removeitem VAR_GUNK_LAST_REPEL, 1
	callnative Gunk_RestartRepel
	playse SE_REPEL
	msgbox Text_GunkUsedAnotherRepel
	waitse
EventScript_GunkRepelWoreOffDone::
	closemessage
	releaseall
	end

EventScript_GunkRepelWoreOffMessage::
	msgbox JpText_RepelWoreOff, MSGBOX_SIGN
	end

Text_GunkRepelWoreOffUseAnother::
	.string "ムシよけスプレーの こうかが きれた！\n"
	.string "{STR_VAR_1}を つかいますか？$"

Text_GunkUsedAnotherRepel::
	.string "{PLAYER}は {STR_VAR_1}を\n"
	.string "つかった！$"

@ Gunk's key items (data/scripts/gunk_key_items.inc), Japanese, without the DexNav
EventScript_GunkOakGivesKeyItems::
	goto_if_set FLAG_GUNK_GOT_KEY_ITEMS, EventScript_GunkKeyItemsEnd
	msgbox Text_GunkOakAlsoGives
	goto EventScript_GunkGiveKeyItems

EventScript_GunkAideGivesKeyItems::
	goto_if_set FLAG_GUNK_GOT_KEY_ITEMS, EventScript_GunkKeyItemsEnd
	msgbox Text_GunkAideAlsoGives
	goto EventScript_GunkGiveKeyItems

EventScript_GunkMomGivesKeyItems::
	goto_if_unset FLAG_SYS_POKEDEX_GET, EventScript_GunkKeyItemsEnd
	goto_if_set FLAG_GUNK_GOT_KEY_ITEMS, EventScript_GunkKeyItemsEnd
	msgbox Text_GunkMomHasKeyItems
EventScript_GunkGiveKeyItems::
	checkitem 52
	goto_if_eq VAR_RESULT, TRUE, EventScript_GunkGiveExpAll
	giveitem 52
	goto_if_eq VAR_RESULT, FALSE, EventScript_GunkKeyItemsEnd
EventScript_GunkGiveExpAll::
	checkitem 53
	goto_if_eq VAR_RESULT, TRUE, EventScript_GunkGotKeyItems
	giveitem 53
	goto_if_eq VAR_RESULT, FALSE, EventScript_GunkKeyItemsEnd
	setflag FLAG_GUNK_EXP_ALL_ON
EventScript_GunkGotKeyItems::
	setflag FLAG_GUNK_GOT_KEY_ITEMS
	msgbox Text_GunkExplainKeyItems
EventScript_GunkKeyItemsEnd::
	return

@ insertions into the Japanese map scripts (the replaced msgbox is redone here)
EventScript_GunkOakLabHook::
	msgbox JpText_OakExplainCatching
	call EventScript_GunkOakGivesKeyItems
	return

EventScript_GunkMomHook::
	msgbox JpText_MomLookingGreat
	call EventScript_GunkMomGivesKeyItems
	return

EventScript_GunkPewterHook::
	call EventScript_GunkAideGivesKeyItems
	msgbox JpText_AideMustBeGoing
	return

Text_GunkAideAlsoGives::
	.string "オーキドはかせから これも\n"
	.string "わたすように たのまれて いたんだ。$"

Text_GunkOakAlsoGives::
	.string "オーキド“それと これも もっていけ！\n"
	.string "たびに きっと やくだつ はずじゃ！$"

Text_GunkMomHasKeyItems::
	.string "{PLAYER}！ オーキドはかせが\n"
	.string "これを おいていったわよ。$"

Text_GunkExplainKeyItems::
	.string "むげんスプレーを オンにすると\n"
	.string "よわい ポケモンが でてこない。\p"
	.string "ぜんいんがくしゅうを オンにすると\n"
	.string "たたかって いない ポケモンも\l"
	.string "けいけんちを はんぶん もらえる。\p"
	.string "どちらも バッグから つかうと\n"
	.string "オンと オフが きりかわる。$"
