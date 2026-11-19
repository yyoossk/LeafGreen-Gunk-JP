#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/items.h"
#include "constants/songs.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.section .rodata
	.align 2

@ セキエイこうげんの ショップ: シルフの しゃちょうから マスターボールを もらったら マスターボールも
EventScript_JpIndigoMart::
	goto_if_set FLAG_GOT_MASTER_BALL_FROM_SILPH, EventScript_JpIndigoMartMB
	pokemart 0x08189754
	return
EventScript_JpIndigoMartMB:
	pokemart JpIndigoItemsMB
	return

	.align 2
JpIndigoItemsMB:
	.2byte ITEM_MASTER_BALL
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_FULL_RESTORE
	.2byte ITEM_MAX_POTION
	.2byte ITEM_REVIVE
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_MAX_REPEL
	.2byte ITEM_NONE

@ そだてや: そだった レベルの あとに いまの レベル
EventScript_JpDaycareGrownFourIsland::
	msgbox 0x081A581B
	callnative JpDaycareLevelFourIsland
	msgbox Text_JpDaycareNowLevel
	return

EventScript_JpDaycareGrownRoute5::
	msgbox 0x0818C60F
	callnative JpDaycareLevelRoute5
	msgbox Text_JpDaycareNowLevel
	return

EventScript_JpDaycareNotYetRoute5::
	msgbox 0x0818C562
	callnative JpDaycareLevelRoute5
	msgbox Text_JpDaycareNowLevel
	return

Text_JpDaycareNowLevel:
	.string "いまは　レベル{STR_VAR_3}だ！$"

@ 殿堂入り: EventScript_SetDefeatedEliteFourFlagsVars のあとに 伝説の ポケモンを もどす
EventScript_JpHoFFlags::
	call 0x08193980
	callnative JpRespawnLegends
	return

@ ボックスの 自動きりかえ と レポート
EventScript_JpBoxSwitched::
	lockall
	playse SE_PC_LOGIN
	msgbox Text_JpBoxSwitched
	message Text_JpBoxSaving
	waitmessage
	callnative JpAutoSaveGame
	end

EventScript_JpBoxSaved::
	playse SE_SAVE
	waitse
	msgbox Text_JpBoxSaved
	releaseall
	end

Text_JpBoxSwitched:
	.string "{STR_VAR_1}が　いっぱいに　なったので\n"
	.string "{STR_VAR_2}に　きりかえた！$"
Text_JpBoxSaving:
	.string "レポートを　かいています\n"
	.string "でんげんを　きらないで　ください$"
Text_JpBoxSaved:
	.string "{PLAYER}は\n"
	.string "レポートに　しっかり　かきのこした！$"

gJpText_SafariHud::
	.string "あと　{STR_VAR_1}ほ　ボール　{STR_VAR_2}こ$"

@ バトルの わざの じょうほう (hk_battle_info.c)
gJpText_BtlPower::
	.string "いりょく$"
gJpText_BtlAccuracy::
	.string "めいちゅう$"
gJpText_BtlFoe::
	.string "あいて$"
gJpText_BtlHp::
	.string "HP$"
gJpText_BtlNoValue::
	.string "ーー$"
gJpText_BtlNone::
	.string "$"
gJpText_BtlSmallFont::
	.string "{FONT_SMALL}$"
JpText_BtlX0:
	.string "×0$"
JpText_BtlX14:
	.string "×1/4$"
JpText_BtlX12:
	.string "×1/2$"
JpText_BtlX1:
	.string "×1$"
JpText_BtlX2:
	.string "×2$"
JpText_BtlX4:
	.string "×4$"
	.align 2
gJpText_BtlEffect::
	.4byte JpText_BtlX0, JpText_BtlX14, JpText_BtlX12, JpText_BtlX1, JpText_BtlX2, JpText_BtlX4

@ ずかんの 種族値と しんか (hk_dex_stats.c)
	.align 2
gJpText_DexStats1::
	.string "HP{STR_VAR_1}　こうげき{STR_VAR_2}　ぼうぎょ{STR_VAR_3}$"
gJpText_DexStats2::
	.string "とくこう{STR_VAR_1}　とくぼう{STR_VAR_2}　すばやさ{STR_VAR_3}$"
gJpText_DexStats3::
	.string "ごうけい{STR_VAR_1}　しんか　$"
gJpText_DexEvoNone::
	.string "なし$"
gJpText_DexEvoLv::
	.string "レベル$"
gJpText_DexEvoTrade::
	.string "つうしんこうかん$"
gJpText_DexEvoFriend::
	.string "なつき$"
gJpText_DexEvoSep::
	.string "/$"
gJpText_DexEvoMore::
	.string "　など$"
