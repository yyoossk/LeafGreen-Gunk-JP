#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/songs.h"
#include "constants/event_objects.h"
#include "constants/event_object_movement.h"
#include "constants/field_effects.h"
#include "constants/field_weather.h"
#include "constants/species.h"
#include "constants/layouts.h"
#include "constants/map_scripts.h"
#include "constants/battle_setup.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.set YES, 1
	.set NO, 0


@ FRLG+ Gym Leader rematches at the Seven Island house (JP port; see src/hooks/hk_battle_house.c)
	.set SET_SPEAROW_STATE, 0
	.set SET_TOLD_FAMECHECKER, 1
	.set SET_VISITOR_STATE, 2
	.set SET_LEVEL_GROWTH, 3
	.set CHECK_SPEAROW_STATE, 4
	.set CHECK_TOLD_FAMECHECKER, 5
	.set CHECK_VISITOR_STATE, 6
	.set CHECK_LEVEL_GROWTH, 7
	.set SET_BOXES_MOVED, 8
	.set CHECK_BOXES_MOVED, 9
	.set CHECK_ANY_VISITORS, 10
	.set CHECK_ALL_TOLD, 11
	.set CREATE_VISITOR_STRING, 12
	.set FIND_TELLABLE, 13
	.set TYPE, VAR_0x8003
	.set ARGUMENT, VAR_0x8004
	.set LEADER, VAR_0x8004
	.set LOCALID, VAR_0x8005
	.set TEXTKIND, VAR_0x8006
	.set LEADER_READY, VAR_TEMP_6
	.set VAR_JP_BATTLE_HOUSE, 0x408C
	.set LOCALID_OLD_WOMAN, 1
	.set LOCALID_SPEAROW, 2
	.set TEXT_INTRO, 0
	.set TEXT_SQUAREUP, 1
	.set TEXT_OTHER, 2
	.set TEXT_DECLINED, 3
	.set TEXT_BEFORE, 4
	.set TEXT_EXIT, 5
	.set JP_FIRST_REMATCH_TRAINER, 743
	.set SPECIAL_HealPlayerParty, 0

	.macro bhvar type:req
	setvar TYPE, \type
	callnative UseBattleHouseVar
	.endm

	@ msgbox with the leader's text of kind \kind (JpBH_LoadLeaderText puts it in the script's data[0])
	.macro leadermsg kind:req, type=MSGBOX_DEFAULT
	setvar TEXTKIND, \kind
	callnative JpBH_LoadLeaderText
	callstd \type
	.endm

	.section .rodata
	.align 2

@ ------------------------------------------------------------------ basement (SevenIsland_House_Room2)
JpRoom2_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, JpRoom2_OnTransition
	.byte 0

JpRoom2_OnTransition::
	setvar LEADER_READY, 0
	callnative JpBH_HideAbsentLeaders
	end

	.macro leaderstub n:req
	.global JpRoom2_EventScript_Leader\n
JpRoom2_EventScript_Leader\n\():
	setvar LEADER, \n
	goto JpRoom2_EventScript_LeaderTalk
	.endm
	leaderstub 0
	leaderstub 1
	leaderstub 2
	leaderstub 3
	leaderstub 4
	leaderstub 5
	leaderstub 6

JpRoom2_EventScript_LeaderTalk::
	lock
	faceplayer
	copyvar LOCALID, LEADER
	addvar LOCALID, 1
	goto_if_eq LEADER_READY, 0, JpRoom2_EventScript_LeaderAsk
	compare LEADER_READY, LOCALID
	goto_if_eq JpRoom2_EventScript_LeaderReady
	leadermsg TEXT_OTHER
	release
	end

JpRoom2_EventScript_LeaderReady::
	leadermsg TEXT_SQUAREUP
	release
	end

JpRoom2_EventScript_LeaderAsk::
	leadermsg TEXT_INTRO, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, JpRoom2_EventScript_LeaderDeclined
	closemessage
	fadescreen FADE_TO_BLACK
	setobjectxyperm LOCALID, 7, 5
	setobjectxy LOCALID, 7, 5
	turnobject LOCALID, DIR_WEST
	setobjectmovementtype LOCALID, MOVEMENT_TYPE_FACE_LEFT
	fadescreen FADE_FROM_BLACK
	copyvar LEADER_READY, LOCALID
	leadermsg TEXT_SQUAREUP
	release
	end

JpRoom2_EventScript_LeaderDeclined::
	leadermsg TEXT_DECLINED
	release
	end

JpBH_ReleaseEnd::
	release
	end

@ the mat in front of the waiting Leader
JpRoom2_EventScript_Trigger::
	goto_if_eq LEADER_READY, 0, JpBH_ReleaseEnd
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, JpRoom2_Movement_FaceRight
	waitmovement 0
	copyvar LOCALID, LEADER_READY
	copyvar LEADER, LEADER_READY
	subvar LEADER, 1
	setvar ARGUMENT, 0
	copyvar ARGUMENT, LEADER
	bhvar SET_VISITOR_STATE
	applymovement LOCALID, JpRoom2_Movement_FaceLeft
	waitmovement 0
	textcolor 0
	leadermsg TEXT_BEFORE
	releaseall
	switch LEADER
	case 0, JpRoom2_EventScript_Battle0
	case 1, JpRoom2_EventScript_Battle1
	case 2, JpRoom2_EventScript_Battle2
	case 3, JpRoom2_EventScript_Battle3
	case 4, JpRoom2_EventScript_Battle4
	case 5, JpRoom2_EventScript_Battle5
	case 6, JpRoom2_EventScript_Battle6
	end

	.macro leaderbattle n:req
JpRoom2_EventScript_Battle\n\():
	trainerbattle_no_intro JP_FIRST_REMATCH_TRAINER + \n, JpRoom2_Text_Loss\n
	goto JpRoom2_EventScript_AfterBattle
	.endm
	leaderbattle 0
	leaderbattle 1
	leaderbattle 2
	leaderbattle 3
	leaderbattle 4
	leaderbattle 5
	leaderbattle 6

JpRoom2_EventScript_AfterBattle::
	copyvar VAR_0x8007, LEADER
	addvar VAR_0x8007, JP_FIRST_REMATCH_TRAINER
	cleartrainerflag VAR_0x8007
	bhvar SET_LEVEL_GROWTH
	lockall
	copyvar LOCALID, LEADER
	addvar LOCALID, 1
	applymovement LOCALID, JpRoom2_Movement_FaceLeft
	waitmovement 0
	textcolor 0
	leadermsg TEXT_EXIT
	applymovement LOCALID, JpRoom2_Movement_LeaderExits
	waitmovement 0
	playse SE_EXIT
	setvar LEADER_READY, 0
	removeobject LOCALID
	releaseall
	end

JpRoom2_Movement_FaceRight::
	walk_in_place_faster_right
	step_end
JpRoom2_Movement_FaceLeft::
	walk_in_place_faster_left
	step_end
JpRoom2_Movement_LeaderExits::
	walk_up
	walk_left
	walk_left
	walk_left
	walk_left
	walk_up
	walk_up
	walk_up
	set_invisible
	step_end

JpRoom2_EventScript_LeftPainting::
	msgbox JpRoom2_Text_LeftPainting, MSGBOX_SIGN
	end
JpRoom2_EventScript_MiddlePainting::
	msgbox JpRoom2_Text_MiddlePainting, MSGBOX_SIGN
	end
JpRoom2_EventScript_RightPainting::
	call_if_eq VAR_STARTER_MON, 0, JpRoom2_EventScript_BufferBulbasaur
	call_if_eq VAR_STARTER_MON, 1, JpRoom2_EventScript_BufferSquirtle
	call_if_ge VAR_STARTER_MON, 2, JpRoom2_EventScript_BufferCharmander
	msgbox JpRoom2_Text_RightPainting, MSGBOX_SIGN
	end
JpRoom2_EventScript_BufferBulbasaur::
	bufferspeciesname STR_VAR_1, SPECIES_VENUSAUR
	bufferspeciesname STR_VAR_2, SPECIES_CHARIZARD
	return
JpRoom2_EventScript_BufferSquirtle::
	bufferspeciesname STR_VAR_1, SPECIES_BLASTOISE
	bufferspeciesname STR_VAR_2, SPECIES_VENUSAUR
	return
JpRoom2_EventScript_BufferCharmander::
	bufferspeciesname STR_VAR_1, SPECIES_CHARIZARD
	bufferspeciesname STR_VAR_2, SPECIES_BLASTOISE
	return

JpRoom2_EventScript_HealingMachine::
	lockall
	msgbox JpRoom2_Text_HealPokemon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, JpRoom2_EventScript_HealEnd
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, JpRoom2_Movement_FaceRight
	waitmovement 0
	delay 24
	dofieldeffect FLDEFF_POKECENTER_HEAL
	waitfieldeffect FLDEFF_POKECENTER_HEAL
	special HealPlayerParty
JpRoom2_EventScript_HealEnd::
	releaseall
	end

@ ------------------------------------------------------------------ the old woman (SevenIsland_House_Room1)
JpRoom1_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, JpRoom1_OnTransition
	.byte 0

JpRoom1_OnTransition::
	bhvar CHECK_BOXES_MOVED
	call_if_eq VAR_RESULT, 1, JpRoom1_EventScript_DoorOpenLayout
	bhvar CHECK_SPEAROW_STATE
	call_if_eq VAR_RESULT, 1, JpRoom1_EventScript_HideSpearow
	bhvar CHECK_ALL_TOLD
	call_if_eq VAR_RESULT, 7, JpRoom1_EventScript_WalkSpearow
	end

JpRoom1_EventScript_DoorOpenLayout::
	setmaplayoutindex LAYOUT_SEVEN_ISLAND_HOUSE_ROOM1_DOOR_OPEN
	return
JpRoom1_EventScript_HideSpearow::
	setflag FLAG_TEMP_1
	return
JpRoom1_EventScript_WalkSpearow::
	setobjectmovementtype LOCALID_SPEAROW, MOVEMENT_TYPE_WANDER_AROUND
	return

JpRoom1_EventScript_OldWoman::
	lock
	faceplayer
	bhvar CHECK_SPEAROW_STATE
	goto_if_eq VAR_RESULT, 1, JpRoom1_EventScript_SpearowGone
	bhvar CHECK_BOXES_MOVED
	goto_if_eq VAR_RESULT, 1, JpRoom1_EventScript_BasementOpen
	msgbox JpRoom1_Text_OnlyEnjoymentWatchingBattles
	goto JpRoom1_EventScript_AskTell

JpRoom1_EventScript_BasementOpen::
	bhvar CHECK_ALL_TOLD
	copyvar VAR_0x8000, VAR_RESULT
	bhvar CREATE_VISITOR_STRING
	goto_if_eq VAR_RESULT, 0, JpRoom1_EventScript_NoVisitors
	msgbox JpRoom1_Text_Visitors
	goto_if_ge VAR_0x8000, 7, JpRoom1_EventScript_ToldAll
	goto JpRoom1_EventScript_AskTell
JpRoom1_EventScript_NoVisitors::
	msgbox JpRoom1_Text_NoVisitors
	goto_if_ge VAR_0x8000, 7, JpRoom1_EventScript_ToldAll
	goto JpRoom1_EventScript_AskTell
JpRoom1_EventScript_ToldAll::
	msgbox JpRoom1_Text_ToldAll
	release
	end

JpRoom1_EventScript_AskTell::
	textcolor 3
	msgbox JpRoom1_Text_ShowFameChecker, MSGBOX_YESNO
	textcolor 1
	goto_if_eq VAR_RESULT, NO, JpRoom1_EventScript_NoShow
	setvar ARGUMENT, 0
	bhvar FIND_TELLABLE
	goto_if_eq VAR_RESULT, FALSE, JpRoom1_EventScript_NobodyToTell
JpRoom1_EventScript_OfferLeader::
	msgbox JpRoom1_Text_TellAbout, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, JpRoom1_EventScript_Tell
	addvar ARGUMENT, 1
	bhvar FIND_TELLABLE
	goto_if_eq VAR_RESULT, TRUE, JpRoom1_EventScript_OfferLeader
	msgbox JpRoom1_Text_NoShow
	release
	end

JpRoom1_EventScript_NoShow::
	msgbox JpRoom1_Text_NoShow
	release
	end

JpRoom1_EventScript_NobodyToTell::
	msgbox JpRoom1_Text_NotEnoughKnown
	release
	end

JpRoom1_EventScript_Tell::
	msgbox JpRoom1_Text_FullFameChecker
	goto_if_ne VAR_JP_BATTLE_HOUSE, 0, JpRoom1_EventScript_InviteBasementOpen
	msgbox JpRoom1_Text_FirstFullFameChecker
	goto JpRoom1_EventScript_SendOutSpearow
JpRoom1_EventScript_InviteBasementOpen::
	msgbox JpRoom1_Text_InviteBasementOpen
JpRoom1_EventScript_SendOutSpearow::
	copyvar VAR_0x8001, VAR_JP_BATTLE_HOUSE
	turnobject LOCALID_OLD_WOMAN, DIR_EAST
	msgbox JpRoom1_Text_CallSpearow
	turnobject LOCALID_SPEAROW, DIR_WEST
	waitse
	playmoncry SPECIES_SPEAROW, 0
	msgbox JpRoom1_Text_Spearow
	waitmoncry
	applymovement LOCALID_SPEAROW, JpRoom1_Movement_SpearowToTable
	waitmovement 0
	playse SE_LEDGE
	applymovement LOCALID_SPEAROW, JpRoom1_Movement_SpearowFinishToTable
	waitmovement 0
	msgbox JpRoom1_Text_DeliverToLeader
	waitse
	playmoncry SPECIES_SPEAROW, 0
	msgbox JpRoom1_Text_Spearow
	waitmoncry
	playse SE_LEDGE
	applymovement LOCALID_SPEAROW, JpRoom1_Movement_SpearowExitHouse
	waitmovement 0
	playse SE_EXIT
	removeobject LOCALID_SPEAROW
	faceplayer
	bhvar SET_SPEAROW_STATE
	bhvar SET_TOLD_FAMECHECKER
	goto_if_ne VAR_0x8001, 0, JpRoom1_EventScript_TakeTime
	msgbox JpRoom1_Text_FirstTakeTime
	release
	end
JpRoom1_EventScript_TakeTime::
	msgbox JpRoom1_Text_TakeTime
	release
	end

JpRoom1_EventScript_SpearowGone::
	msgbox JpRoom1_Text_SpearowNotBackYet
	release
	end

JpRoom1_EventScript_Spearow::
	lock
	faceplayer
	waitse
	playmoncry SPECIES_SPEAROW, 0
	msgbox JpRoom1_Text_Spearow
	waitmoncry
	release
	end

JpRoom1_Movement_SpearowToTable::
	walk_fast_up
	walk_fast_up
	walk_fast_left
	walk_fast_left
	step_end
JpRoom1_Movement_SpearowFinishToTable::
	jump_left
	walk_left
	step_end
JpRoom1_Movement_SpearowExitHouse::
	jump_2_down
	walk_fast_left
	walk_fast_down
	delay_8
	set_invisible
	step_end

@ ------------------------------------------------------------------ the mailbox outside
JpSevenIsland_EventScript_Mailbox::
	bhvar CHECK_BOXES_MOVED
	goto_if_eq VAR_RESULT, 0, JpSevenIsland_EventScript_FadedWriting
	bhvar CREATE_VISITOR_STRING
	goto_if_eq VAR_RESULT, 0, JpSevenIsland_EventScript_NoVisitors
	msgbox JpSevenIsland_Text_BattleHouseVisitors, MSGBOX_SIGN
	end
JpSevenIsland_EventScript_NoVisitors::
	msgbox JpSevenIsland_Text_BattleHouseNoVisitors, MSGBOX_SIGN
	end
JpSevenIsland_EventScript_FadedWriting::
	msgbox JpSevenIsland_Text_FadedWriting, MSGBOX_SIGN
	end

@ ------------------------------------------------------------------ texts
JpRoom2_Text_LeftPainting::
	.string "わかい おんなの ひとの しゃしんだ\n"
	.string "つよそうな ポケモンたちに\l"
	.string "かこまれて わらっている$"
JpRoom2_Text_MiddlePainting::
	.string "わかい おんなの ひとの しゃしんだ\n"
	.string "うでに オニスズメが とまっている$"
JpRoom2_Text_RightPainting::
	.string "トレーナー どうしの\n"
	.string "しょうぶの しゃしんだ\p"
	.string "わかい おんなの ひとの\n"
	.string "{STR_VAR_1}が あいての\l"
	.string "{STR_VAR_2}に こうげき している\p"
	.string "うえでは オニスズメが\n"
	.string "しょうぶを じっと みている$"
JpRoom2_Text_HealPokemon::
	.string "きかいで ポケモンを\n"
	.string "かいふく しますか？$"

JpRoom1_Text_OnlyEnjoymentWatchingBattles::
	.string "いまは こんな だけど\n"
	.string "わかい ころは ねえ……\p"
	.string "あちこち とびまわっては\n"
	.string "トレーナーに しょうぶを\l"
	.string "いどんだ ものさ\p"
	.string "いまの たのしみは むかしを\n"
	.string "おもいだしながら つよい\l"
	.string "トレーナーの しょうぶを\l"
	.string "ながめる ことくらいだよ\p"
	.string "おや その バッジ……\n"
	.string "カントーの ジムを ぜんぶ\l"
	.string "やぶったのかい？\p"
	.string "なら たびの とちゅうで\n"
	.string "つよい トレーナーに\l"
	.string "たくさん あったろう？\p"
	.string "たいくつな ばあさんに\n"
	.string "はなしを きかせて おくれ$"
JpRoom1_Text_ShowFameChecker::
	.string "ゆうめいじん チェッカーを\n"
	.string "みせますか？$"
JpRoom1_Text_NoShow::
	.string "そうかい……\n"
	.string "また はなしを きかせて おくれ$"
JpRoom1_Text_NotEnoughKnown::
	.string "うーん……\p"
	.string "どの トレーナーも まだ\n"
	.string "どんな しょうぶを するのか\l"
	.string "よく わからないねえ\p"
	.string "もっと くわしく しらべたら\n"
	.string "また みせて おくれ$"
JpRoom1_Text_TellAbout::
	.string "{STR_VAR_1}の ことを\n"
	.string "はなしますか？$"
JpRoom1_Text_FullFameChecker::
	.string "……！\p"
	.string "{STR_VAR_1}かい！\n"
	.string "まさに わたしの みたい\l"
	.string "しょうぶを する トレーナーだね$"
JpRoom1_Text_FirstFullFameChecker::
	.string "ひとつ おしえて あげよう\n"
	.string "この いえには ちかしつが あるんだ\p"
	.string "むかしは そこで ポケモンを\n"
	.string "きたえたり ひとを まねいて\l"
	.string "しょうぶ したり したものさ\p"
	.string "ちかしつを また ひらいて\n"
	.string "{STR_VAR_1}を まねいて みよう$"
JpRoom1_Text_InviteBasementOpen::
	.string "さっそく {STR_VAR_1}に\n"
	.string "しょうたいじょうを だそう！$"
JpRoom1_Text_CallSpearow::
	.string "オニスズメや！\n"
	.string "ちょっと おいで！$"
JpRoom1_Text_Spearow::
	.string "オニスズメ“ピピーッ！$"
JpRoom1_Text_DeliverToLeader::
	.string "この しょうたいじょうを\n"
	.string "{STR_VAR_3}ジムの {STR_VAR_1}に\l"
	.string "とどけて おくれ！$"
JpRoom1_Text_FirstTakeTime::
	.string "オニスズメが へんじを もって\n"
	.string "かえるまで しばらく かかるよ\p"
	.string "ここで まって いなくても いい\n"
	.string "また あとで きて おくれ\p"
	.string "その あいだに ちかしつの\n"
	.string "したくを して おくからね$"
JpRoom1_Text_TakeTime::
	.string "オニスズメが へんじを もって\n"
	.string "かえるまで しばらく かかるよ\p"
	.string "ここで まって いなくても いい\n"
	.string "また あとで きて おくれ$"
JpRoom1_Text_SpearowNotBackYet::
	.string "オニスズメが まだ もどらないんだ\n"
	.string "へんじは もう すこし まっとくれ$"
JpRoom1_Text_NoVisitors::
	.string "おや {PLAYER}\n"
	.string "しゅぎょうに きたのかい？\p"
	.string "いまは ちかしつに だれも\n"
	.string "きて いないよ$"
JpRoom1_Text_Visitors::
	.string "おや {PLAYER}\n"
	.string "しゅぎょうに きたのかい？\p"
	.string "いまは ちかしつに\n"
	.string "{STR_VAR_1}が きて いるよ$"
JpRoom1_Text_ToldAll::
	.string "あんたの おかげで また\n"
	.string "すばらしい しょうぶを たくさん\l"
	.string "みられるように なったよ\p"
	.string "ほんとうに ありがとうね$"

JpSevenIsland_Text_FadedWriting::
	.string "ポストに うすれた もじが\n"
	.string "かいてある……\p"
	.string "“バトル……ウス”$"
JpSevenIsland_Text_BattleHouseNoVisitors::
	.string "バトルハウス\n"
	.string "いまは だれも いないようだ$"
JpSevenIsland_Text_BattleHouseVisitors::
	.string "バトルハウス\n"
	.string "いまは {STR_VAR_1}が\l"
	.string "きて いるようだ$"

@ the Leaders: intro (yes/no), square up, another Leader is waiting, declined, before the battle, after
	.align 2
gJpLeaderTexts::
	.4byte JpRoom2_Text_BrockIntro, JpRoom2_Text_BrockSquareUp, JpRoom2_Text_BrockOther, JpRoom2_Text_BrockDeclined, JpRoom2_Text_BrockBefore, JpRoom2_Text_BrockExit
	.4byte JpRoom2_Text_MistyIntro, JpRoom2_Text_MistySquareUp, JpRoom2_Text_MistyOther, JpRoom2_Text_MistyDeclined, JpRoom2_Text_MistyBefore, JpRoom2_Text_MistyExit
	.4byte JpRoom2_Text_SurgeIntro, JpRoom2_Text_SurgeSquareUp, JpRoom2_Text_SurgeOther, JpRoom2_Text_SurgeDeclined, JpRoom2_Text_SurgeBefore, JpRoom2_Text_SurgeExit
	.4byte JpRoom2_Text_ErikaIntro, JpRoom2_Text_ErikaSquareUp, JpRoom2_Text_ErikaOther, JpRoom2_Text_ErikaDeclined, JpRoom2_Text_ErikaBefore, JpRoom2_Text_ErikaExit
	.4byte JpRoom2_Text_KogaIntro, JpRoom2_Text_KogaSquareUp, JpRoom2_Text_KogaOther, JpRoom2_Text_KogaDeclined, JpRoom2_Text_KogaBefore, JpRoom2_Text_KogaExit
	.4byte JpRoom2_Text_SabrinaIntro, JpRoom2_Text_SabrinaSquareUp, JpRoom2_Text_SabrinaOther, JpRoom2_Text_SabrinaDeclined, JpRoom2_Text_SabrinaBefore, JpRoom2_Text_SabrinaExit
	.4byte JpRoom2_Text_BlaineIntro, JpRoom2_Text_BlaineSquareUp, JpRoom2_Text_BlaineOther, JpRoom2_Text_BlaineDeclined, JpRoom2_Text_BlaineBefore, JpRoom2_Text_BlaineExit

JpRoom2_Text_BrockIntro::
	.string "タケシ“……はじめて あった ときとは\n"
	.string "まるで ちがうな！\p"
	.string "チャンピオンに なった\n"
	.string "きみに たのみが あるんだ\p"
	.string "じつは ジムリーダーには\n"
	.string "チャンピオンに ちょうせん する\l"
	.string "けんりが あるんだよ！\p"
	.string "……もう いちど\n"
	.string "しょうぶ させて くれないか！\p"
	.string "おれの ポケモンの\n"
	.string "ほんとうの かたさを みせよう！$"
JpRoom2_Text_BrockSquareUp::
	.string "タケシ“そっちに たって くれ\n"
	.string "しょうぶを はじめよう！$"
JpRoom2_Text_BrockOther::
	.string "タケシ“ほかの ジムリーダーを\n"
	.string "あまく みるなよ {PLAYER}\p"
	.string "チャンピオンには みんな\n"
	.string "とっておきの ポケモンで いどむぞ！$"
JpRoom2_Text_BrockDeclined::
	.string "タケシ“そうか……\n"
	.string "なら おれたちは もっと\l"
	.string "かたく つよく なって おくよ！$"
JpRoom2_Text_BrockBefore::
	.string "タケシ“どんな あいてでも\n"
	.string "おれの いわタイプは うけてたつ！\p"
	.string "それが おれの かたい\n"
	.string "いしの ちかいだ！$"
JpRoom2_Text_BrockExit::
	.string "タケシ“ほかの ゆめも あるけど\n"
	.string "すこし あとまわしに したんだ\p"
	.string "いまは きみに かてるくらい\n"
	.string "つよく なりたいんだよ！\p"
	.string "そろそろ ジムに もどるよ\n"
	.string "つぎの しょうぶを たのしみに してる$"
JpRoom2_Text_Loss0::
	.string "つよいとは おもっていたが\n"
	.string "これほどとは……$"

JpRoom2_Text_MistyIntro::
	.string "カスミ“おもしろい うわさを\n"
	.string "きいたわよ！\p"
	.string "ロケットだんを やっつけた うえに\n"
	.string "マサラタウンの あの こにも かって\l"
	.string "チャンピオンに なったって！\p"
	.string "もう！ がまん できない！\p"
	.string "ぜったい もう いちど\n"
	.string "しょうぶ してもらうわよ！\l"
	.string "ことわるのは なしだからね！$"
JpRoom2_Text_MistySquareUp::
	.string "カスミ“わたしの むかいに たって！\n"
	.string "はじめるわよ！$"
JpRoom2_Text_MistyOther::
	.string "カスミ“しょうぶを みるのが すきなのは\n"
	.string "うえの おばあさん だけじゃないの\p"
	.string "みずタイプを どう あつかうか\n"
	.string "みせて ほしいわね！$"
JpRoom2_Text_MistyDeclined::
	.string "カスミ“ことわるのは なしって\n"
	.string "いったのに！ もう いいわよ……\p"
	.string "つぎ たたかう ときは\n"
	.string "ぜったい まけないんだから！$"
JpRoom2_Text_MistyBefore::
	.string "カスミ“わたしの かわいい ポケモンが\n"
	.string "あいてに なるわ！\p"
	.string "みずタイプの さいきょうの こうげき！\n"
	.string "かくご しなさい！$"
JpRoom2_Text_MistyExit::
	.string "カスミ“まけちゃった……\p"
	.string "ジムで すこし およいで\n"
	.string "きもちを きりかえなくちゃ\p"
	.string "……つぎは ぜったい まけないわよ！$"
JpRoom2_Text_Loss1::
	.string "もう！\n"
	.string "くやしいったら ないわ！$"

JpRoom2_Text_SurgeIntro::
	.string "マチス“ヘイ ボーイ！\p"
	.string "ポケモンリーグを とっぱ するとは\n"
	.string "まったく シビれる はなしだ！\p"
	.string "でんきタイプの ちからも\n"
	.string "かりたんだろう？\p"
	.string "よし！ きみが そだてた\n"
	.string "ポケモンを みせて もらおうか！$"
JpRoom2_Text_SurgeSquareUp::
	.string "マチス“せいれつ！ きみの ポケモンを\n"
	.string "しびれさせて やるぜ！$"
JpRoom2_Text_SurgeOther::
	.string "マチス“ほかの リーダーは ミーほど\n"
	.string "きびしく ないが しゅぎょうは\l"
	.string "おなじくらい しているぞ！$"
JpRoom2_Text_SurgeDeclined::
	.string "マチス“ハハハ！ しびれるのが\n"
	.string "こわいのかい？$"
JpRoom2_Text_SurgeBefore::
	.string "マチス“ミーたちに ことばは いらない！\n"
	.string "いくぜ ボーイ！$"
JpRoom2_Text_SurgeExit::
	.string "マチス“まだ うでの さが あるようだ！\p"
	.string "こんな きもちは くにを でて\n"
	.string "はじめてだぜ！\p"
	.string "きちに もどらなくては！\n"
	.string "ぶかを ほうって おけないからな！$"
JpRoom2_Text_Loss2::
	.string "まったく\n"
	.string "シビれる ぜ！$"

JpRoom2_Text_ErikaIntro::
	.string "エリカ“あら ずかんを うめようと\n"
	.string "されている かた ですわね\p"
	.string "おかわり ありません こと？\p"
	.string "……そうですの いそがしく\n"
	.string "されて いますのね\p"
	.string "でも しょうぶは べつ ですわ\n"
	.string "その ために いらしたの でしょう？$"
JpRoom2_Text_ErikaSquareUp::
	.string "エリカ“あちらに おたち ください\n"
	.string "はじめましょう$"
JpRoom2_Text_ErikaOther::
	.string "エリカ“……すう……すう……\n"
	.string "あら しょうぶの ごよういを？$"
JpRoom2_Text_ErikaDeclined::
	.string "エリカ“…… …… …… ……$"
JpRoom2_Text_ErikaBefore::
	.string "エリカ“ちょうせん おうけ いたします\n"
	.string "まけは しませんわ！$"
JpRoom2_Text_ErikaExit::
	.string "エリカ“すばらしい ですわ\p"
	.string "レインボーバッジ\n"
	.string "10こぶんの しょうぶ でしたわ\p"
	.string "タマムシに もどって\n"
	.string "おはなの おせわを しなくては\p"
	.string "……また おあい しましょう$"
JpRoom2_Text_Loss3::
	.string "あら……\n"
	.string "わたくしの まけ ですわね……$"

JpRoom2_Text_KogaIntro::
	.string "キョウ“ファファファ！\n"
	.string "おまえか こぞう\p"
	.string "なんども あう さだめの ようだな\p"
	.string "ちょうど みがいた わざを\n"
	.string "ためしたいと おもって いたところだ\l"
	.string "おまえを たおす しょうぶでな！\p"
	.string "ファファファ！ どうする？$"
JpRoom2_Text_KogaSquareUp::
	.string "キョウ“かくご しろ こぞう！$"
JpRoom2_Text_KogaOther::
	.string "キョウ“むすめを つれてきて ほかの\n"
	.string "リーダーの たたかいを\l"
	.string "まなばせたい ものだ$"
JpRoom2_Text_KogaDeclined::
	.string "キョウ“なに？ ふん\n"
	.string "その かくごで よく リーグを\l"
	.string "せいは できた ものだ$"
JpRoom2_Text_KogaBefore::
	.string "キョウ“ファファファ！\n"
	.string "きょうは おまえを たおして\l"
	.string "むすめに ちちの いげんを みせよう！$"
JpRoom2_Text_KogaExit::
	.string "キョウ“おまえや {RIVAL}が いる\n"
	.string "ポケモンリーグは つよい ばしょだ\l"
	.string "ほこらしい ことよ！\p"
	.string "わしも してんのうを\n"
	.string "めざそうかと かんがえて おるが\p"
	.string "ジムリーダーの つとめを\n"
	.string "おろそかには できん！\p"
	.string "セキチクに もどるとしよう\n"
	.string "さらばだ こぞう$"
JpRoom2_Text_Loss4::
	.string "いまの わしで かてぬなら\n"
	.string "わざを みがく のみ$"

JpRoom2_Text_SabrinaIntro::
	.string "ナツメ“……エスパーの ちからは\n"
	.string "たしかに つよい\p"
	.string "でも その ちからだけでは\n"
	.string "のりこえられない ものも ある\p"
	.string "まえの しょうぶで まけて\n"
	.string "やっと わかったの\p"
	.string "こんどは ちょうのうりょく だけには\n"
	.string "たよらない\p"
	.string "わたしの ほんとうの ちから……\n"
	.string "ためさせて もらうわ！$"
JpRoom2_Text_SabrinaSquareUp::
	.string "ナツメ“あなたは そこに たつ\n"
	.string "さだめよ$"
JpRoom2_Text_SabrinaOther::
	.string "ナツメ“みらいを みなくても\n"
	.string "この しょうぶの ゆくえは わかるわ$"
JpRoom2_Text_SabrinaDeclined::
	.string "ナツメ“ことわるのは よちして いたわ\n"
	.string "でも いずれ また たたかう$"
JpRoom2_Text_SabrinaBefore::
	.string "ナツメ“ここで あう ことは\n"
	.string "みらいを みて しっていた\p"
	.string "でも どちらが かつかは\n"
	.string "わざと みなかったの\p"
	.string "いっしょに たしかめましょう！$"
JpRoom2_Text_SabrinaExit::
	.string "ナツメ“まえは まけて おどろいた\n"
	.string "でも いまは ちがう\p"
	.string "あなたの ように つよく\n"
	.string "じゆうに いきたいと おもうの\p"
	.string "そろそろ ジムに もどらないと\n"
	.string "ちょうせんしゃを のがして しまう\p"
	.string "しんぱい しないで {PLAYER}\n"
	.string "また すぐに たたかえるわ$"
JpRoom2_Text_Loss5::
	.string "あなたの ような トレーナーには\n"
	.string "あと 3ねんは あえないわね$"

JpRoom2_Text_BlaineIntro::
	.string "カツラ“ハッハッハ！ チャンピオンに\n"
	.string "なるとは よく やった！\p"
	.string "ここで ほかの リーダーと\n"
	.string "しゅぎょう しておるが グレンを\l"
	.string "ながく あけては おけんのだ\p"
	.string "ジムの したの かざんが\n"
	.string "めを さましそうでな！\p"
	.string "だが せっかく きたのだ\n"
	.string "あつい しょうぶを しようではないか！$"
JpRoom2_Text_BlaineSquareUp::
	.string "カツラ“さあ かまえろ\n"
	.string "ちょうせんしゃ！$"
JpRoom2_Text_BlaineOther::
	.string "カツラ“リーダー どうしで よく\n"
	.string "たたかうが れんしゅうの ばしょが\l"
	.string "できたのは ありがたい$"
JpRoom2_Text_BlaineDeclined::
	.string "カツラ“なんと！ わしは もう\n"
	.string "もえあがって おるのに！$"
JpRoom2_Text_BlaineBefore::
	.string "カツラ“クイズだ！ はいに なるのは\n"
	.string "どちらの ポケモンかな？$"
JpRoom2_Text_BlaineExit::
	.string "カツラ“ハッハッハ！ みごとな しょうぶ！\p"
	.string "もっと つよく なりたいと いう\n"
	.string "ほのおが もえて おるわ！\p"
	.string "グレンの かざんは ひに ひに\n"
	.string "かっぱつに なっておる\p"
	.string "もどって みはって おかねば$"
JpRoom2_Text_Loss6::
	.string "……どうやら わしの\n"
	.string "ほうだったな ハッハッハ！$"
