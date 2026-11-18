#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/songs.h"
#include "constants/species.h"
#include "constants/items.h"
#include "constants/battle.h"
#include "constants/event_objects.h"
#include "constants/sound.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set YES, 1
	.set TRUE, 1
	.set FALSE, 0
	.set NO, 0
	.set SPECIAL_GetBattleOutcome, 180
	.set SPECIAL_StartLegendaryBattle, 312

@ 151匹揃う版: unused flags / vars (save compatible)
	.set FLAG_V151_GOT_BULBASAUR, 0x0F0
	.set FLAG_V151_GOT_CHARMANDER, 0x0F1
	.set FLAG_V151_GOT_SQUIRTLE, 0x0F2
	.set FLAG_V151_CAUGHT_MEW, 0x0F7
	.set VAR_V151_EEVEE_COUNT, 0x40A0

@ JP ROM addresses
	.set JP_GetGiftMonPartySlot, 0x08195D69
	.set JP_ChangePokemonNickname, 0x0819462D
	.set JP_NameReceivedBoxMon, 0x08195D75
	.set JP_TransferredToPC, 0x08195D7E
	.set JP_NoMoreRoomForPokemon, 0x081963B9
	.set JP_Text_GiveNickname, 0x08192F52
	.set JP_Text_ObtainedAnEevee, 0x08184927
	.set JP_Text_YouWantDome, 0x08163DF7
	.set JP_Text_ObtainedDome, 0x08163E21
	.set JP_Text_YouWantHelix, 0x08163E05
	.set JP_Text_ObtainedHelix, 0x08163E12
	.set JP_Text_MansionDiary, 0x0816882B
	.set JP_Text_WhichPrize, 0x08185AE8
	.set JP_Prize_Abra, 0x0818561F
	.set JP_Prize_Clefairy, 0x0818562F
	.set JP_Prize_Dratini, 0x0818563F
	.set JP_Prize_Scyther, 0x0818564F
	.set JP_Prize_Porygon, 0x0818565F
	.set JP_Prize_End, 0x0818561A
	.set JP_Prize_Confirm, 0x0818566F
	.set JP_ITEM_DOME_FOSSIL, 0x166
	.set JP_ITEM_HELIX_FOSSIL, 0x165

	.section .v151data, "a"
	.align 2

@ ---------------------------------------------------------------- Eevee x3 (Celadon condo roof)
V151_EventScript_EeveeBall::
	lock
	faceplayer
	setvar VAR_TEMP_1, SPECIES_EEVEE
	givemon SPECIES_EEVEE, 25
	goto_if_eq VAR_RESULT, 0, V151_Eevee_Party
	goto_if_eq VAR_RESULT, 1, V151_Eevee_PC
	goto_if_eq VAR_RESULT, 2, JP_NoMoreRoomForPokemon
	release
	end
V151_Eevee_Party:
	addvar VAR_V151_EEVEE_COUNT, 1
	call V151_Eevee_Fanfare
	goto_if_eq VAR_RESULT, NO, V151_Eevee_Set
	call JP_GetGiftMonPartySlot
	call JP_ChangePokemonNickname
	goto V151_Eevee_Set
V151_Eevee_PC:
	addvar VAR_V151_EEVEE_COUNT, 1
	call V151_Eevee_Fanfare
	goto_if_eq VAR_RESULT, NO, V151_Eevee_ToPC
	call JP_NameReceivedBoxMon
V151_Eevee_ToPC:
	call JP_TransferredToPC
V151_Eevee_Set:
	goto_if_lt VAR_V151_EEVEE_COUNT, 3, V151_Eevee_More
	removeobject VAR_LAST_TALKED
	setflag FLAG_GOT_EEVEE
	release
	end
V151_Eevee_More:
	msgbox V151_Text_EeveeMore
	release
	end
V151_Eevee_Fanfare:
	playfanfare MUS_LEVEL_UP
	message JP_Text_ObtainedAnEevee
	waitmessage
	waitfanfare
	bufferspeciesname STR_VAR_1, SPECIES_EEVEE
	msgbox JP_Text_GiveNickname, MSGBOX_YESNO
	return

V151_Text_EeveeMore:
	.string "モンスターボールは まだ のこっている！$"

@ ---------------------------------------------------------------- Mt. Moon: both fossils
V151_EventScript_DomeFossil::
	lock
	faceplayer
	msgbox JP_Text_YouWantDome, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, V151_Fossil_No
	removeobject 1
	giveitem_msg JP_Text_ObtainedDome, JP_ITEM_DOME_FOSSIL, 1, MUS_OBTAIN_KEY_ITEM
	call V151_Fossil_Both
	removeobject 2
	giveitem_msg JP_Text_ObtainedHelix, JP_ITEM_HELIX_FOSSIL, 1, MUS_OBTAIN_KEY_ITEM
	goto V151_Fossil_Done
V151_Fossil_Both:
	closemessage
	delay 10
	textcolor NPC_TEXT_COLOR_MALE
	msgbox V151_Text_BothFossils
	closemessage
	return
V151_Fossil_Done:
	setflag FLAG_GOT_DOME_FOSSIL
	setflag FLAG_GOT_HELIX_FOSSIL
	setflag FLAG_GOT_FOSSIL_FROM_MT_MOON
	release
	end
V151_EventScript_HelixFossil::
	lock
	faceplayer
	msgbox JP_Text_YouWantHelix, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, V151_Fossil_No
	removeobject 2
	giveitem_msg JP_Text_ObtainedHelix, JP_ITEM_HELIX_FOSSIL, 1, MUS_OBTAIN_KEY_ITEM
	call V151_Fossil_Both
	removeobject 1
	giveitem_msg JP_Text_ObtainedDome, JP_ITEM_DOME_FOSSIL, 1, MUS_OBTAIN_KEY_ITEM
	goto V151_Fossil_Done
V151_Fossil_No:
	release
	end

V151_Text_BothFossils:
	.string "まあ いいか！\p"
	.string "カセキは ふたつとも\n"
	.string "おまえに やるよ！$"

@ ---------------------------------------------------------------- Pokémon Mansion B1F diary: Mew Lv50
V151_EventScript_MewDiary::
	lockall
	msgbox JP_Text_MansionDiary
	goto_if_set FLAG_V151_CAUGHT_MEW, V151_Mew_End
	message V151_Text_MewAppears
	waitmessage
	playmoncry SPECIES_MEW, CRY_MODE_ENCOUNTER
	waitmoncry
	delay 20
	waitbuttonpress
	closemessage
	setwildbattle SPECIES_MEW, 50
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special StartLegendaryBattle
	waitstate
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, V151_Mew_End
	setflag FLAG_V151_CAUGHT_MEW
V151_Mew_End:
	releaseall
	end

V151_Text_MewAppears:
	.string "…… ページの あいだから\n"
	.string "なにかが とびだしてきた！$"

@ ---------------------------------------------------------------- Game Corner: Pinsir 2500 coins
V151_EventScript_ChoosePrizeMon::
	message JP_Text_WhichPrize
	waitmessage
	multichoice 11, 0, 14, FALSE
	copyvar VAR_0x8000, VAR_RESULT
	goto_if_eq VAR_0x8000, 0, JP_Prize_Abra
	goto_if_eq VAR_0x8000, 1, JP_Prize_Clefairy
	goto_if_eq VAR_0x8000, 2, V151_Prize_Pinsir
	goto_if_eq VAR_0x8000, 3, JP_Prize_Dratini
	goto_if_eq VAR_0x8000, 4, JP_Prize_Scyther
	goto_if_eq VAR_0x8000, 5, JP_Prize_Porygon
	goto JP_Prize_End
V151_Prize_Pinsir:
	setvar VAR_TEMP_1, SPECIES_PINSIR
	setvar VAR_TEMP_2, 2500
	goto JP_Prize_Confirm

@ ---------------------------------------------------------------- Celadon 4F: Moon Stone 2100
	.align 1
V151_Mart_Celadon4F::
	.2byte 80, 132, 95, 96, 97, 98, ITEM_MOON_STONE, 0

@ ---------------------------------------------------------------- Bulbasaur / Charmander / Squirtle Lv10
	.macro v151_gift name:req, species:req, flag:req, offer:req, after:req, got:req
	.global V151_EventScript_\name
V151_EventScript_\name\():
	lock
	faceplayer
	goto_if_set \flag, V151_\name\()_After
	.ifc \name, Squirtle
	goto_if_unset FLAG_BADGE03_GET, V151_\name\()_NoBadge
	.endif
	msgbox \offer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, V151_\name\()_Declined
	setvar VAR_TEMP_1, \species
	givemon \species, 10
	goto_if_eq VAR_RESULT, 0, V151_\name\()_Party
	goto_if_eq VAR_RESULT, 1, V151_\name\()_PC
	goto_if_eq VAR_RESULT, 2, JP_NoMoreRoomForPokemon
	release
	end
V151_\name\()_Party:
	call V151_\name\()_Fanfare
	goto_if_eq VAR_RESULT, NO, V151_\name\()_Set
	call JP_GetGiftMonPartySlot
	call JP_ChangePokemonNickname
	goto V151_\name\()_Set
V151_\name\()_PC:
	call V151_\name\()_Fanfare
	goto_if_eq VAR_RESULT, NO, V151_\name\()_ToPC
	call JP_NameReceivedBoxMon
V151_\name\()_ToPC:
	call JP_TransferredToPC
V151_\name\()_Set:
	setflag \flag
V151_\name\()_After:
	msgbox \after
	release
	end
V151_\name\()_Declined:
	msgbox V151_Text_Declined
	release
	end
V151_\name\()_Fanfare:
	playfanfare MUS_LEVEL_UP
	message \got
	waitmessage
	waitfanfare
	bufferspeciesname STR_VAR_1, \species
	msgbox JP_Text_GiveNickname, MSGBOX_YESNO
	return
	.endm

	v151_gift Bulbasaur, SPECIES_BULBASAUR, FLAG_V151_GOT_BULBASAUR, V151_Text_BulbaOffer, V151_Text_BulbaAfter, V151_Text_GotBulba
	v151_gift Charmander, SPECIES_CHARMANDER, FLAG_V151_GOT_CHARMANDER, V151_Text_CharOffer, V151_Text_CharAfter, V151_Text_GotChar
	v151_gift Squirtle, SPECIES_SQUIRTLE, FLAG_V151_GOT_SQUIRTLE, V151_Text_SquirtOffer, V151_Text_SquirtAfter, V151_Text_GotSquirt

V151_Squirtle_NoBadge:
	msgbox V151_Text_SquirtNoBadge
	release
	end

V151_Text_Declined:
	.string "そう……\n"
	.string "きが かわったら また きてね$"

V151_Text_BulbaOffer:
	.string "この フシギダネ……\n"
	.string "わたしじゃ うまく そだてられなくて\p"
	.string "あなたなら だいじに して\n"
	.string "くれそうね！\p"
	.string "フシギダネを つれていって\n"
	.string "くれる？$"
V151_Text_GotBulba:
	.string "{PLAYER}は\n"
	.string "フシギダネを もらった！$"
V151_Text_BulbaAfter:
	.string "フシギダネ げんきに してる？\n"
	.string "だいじに してあげてね！$"

V151_Text_CharOffer:
	.string "おまえ つよいな！\n"
	.string "ゴールデンボールブリッジを\p"
	.string "ぬけてくるとは たいしたもんだ\p"
	.string "この ヒトカゲ……\n"
	.string "おれには てに おえないんだ\p"
	.string "おまえみたいな つよい トレーナーに\n"
	.string "そだてて ほしいんだ！\p"
	.string "もらって くれるか？$"
V151_Text_GotChar:
	.string "{PLAYER}は\n"
	.string "ヒトカゲを もらった！$"
V151_Text_CharAfter:
	.string "ヒトカゲの しっぽの ほのおは\n"
	.string "げんきの しるし なんだぜ！$"

V151_Text_SquirtNoBadge:
	.string "この ゼニガメ いたずらばかりで\n"
	.string "こまってるの\p"
	.string "クチバジムの バッジを もっている\n"
	.string "トレーナーなら まかせられるのに……$"
V151_Text_SquirtOffer:
	.string "それは オレンジバッジ！\p"
	.string "あなたなら まかせられるわ\p"
	.string "この ゼニガメを\n"
	.string "つれていって くれる？$"
V151_Text_GotSquirt:
	.string "{PLAYER}は\n"
	.string "ゼニガメを もらった！$"
V151_Text_SquirtAfter:
	.string "ゼニガメ いいこに してる？\n"
	.string "あなたに まかせて よかったわ！$"
