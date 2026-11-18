#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/songs.h"
#include "constants/event_objects.h"
#include "constants/event_object_movement.h"
#include "constants/species.h"
#include "constants/map_scripts.h"
#include "constants/battle_setup.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.set YES, 1
	.set NO, 0

@ FRLG+ Master Trainers (JP port; see src/hooks/hk_master.c)
	.set TRAINER, VAR_0x8009
	.set CLASS, VAR_0x8006
	.set HAVE_TITLE, VAR_0x8007
	.set TEXTKIND, VAR_0x8005
	.set JP_MASTER_BASE, 750
	.set RIVAL_BATTLE_HEAL_AFTER, 1
	.set T_INTRO, 0
	.set T_NOMON, 1
	.set T_ASK, 2
	.set T_ASKT, 3
	.set T_DECLINED, 4
	.set T_ACCEPTED, 5
	.set T_LOST, 6
	.set T_AFTERWON, 7
	.set T_GIVETITLE, 8
	.set T_ANOTHER, 9
	.set FLAG_JP_OAK_WON_NOW, FLAG_TEMP_1E

	@ msgbox with the class text of kind \kind (JpMaster_LoadText puts it in the script's data[0])
	.macro mmsg kind:req, type=MSGBOX_DEFAULT
	setvar TEXTKIND, \kind
	callnative JpMaster_LoadText
	callstd \type
	.endm

	.section .rodata
	.align 2
	.include "data/hooks/master_gen.inc"

@ new overworld graphics infos: gfx 160-169 Master Trainers, 170 Scott, 171 Sudowoodo (filled in by tools/patch_port.py)
	.global gJpMasterGfxPtrs
	.align 2
gJpMasterGfxPtrs:
	.fill 12, 4, 0

JpMaster_EventScript_Pre::
	lock
	faceplayer
	bufferspeciesname STR_VAR_1, TRAINER
	callnative JpMaster_Prepare
	mmsg T_INTRO
	callnative JpMaster_CheckSlot1
	goto_if_ne VAR_RESULT, TRUE, JpMaster_EventScript_NoMon
	goto_if_eq HAVE_TITLE, TRUE, JpMaster_EventScript_AskAgain
	mmsg T_ASK, MSGBOX_YESNO
	goto JpMaster_EventScript_Asked
JpMaster_EventScript_AskAgain:
	mmsg T_ASKT, MSGBOX_YESNO
JpMaster_EventScript_Asked:
	goto_if_ne VAR_RESULT, YES, JpMaster_EventScript_Declined
	mmsg T_ACCEPTED
	closemessage
	callnative JpMaster_SetupParty
	return

JpMaster_EventScript_NoMon:
	mmsg T_NOMON
	release
	end

JpMaster_EventScript_Declined:
	mmsg T_DECLINED
	release
	end

JpMaster_EventScript_Post::
	callnative JpMaster_GetLost
	copyvar VAR_0x8004, VAR_RESULT
	callnative LoadPlayerParty
	bufferspeciesname STR_VAR_1, TRAINER
	callnative JpMaster_Prepare
	goto_if_eq VAR_0x8004, TRUE, JpMaster_EventScript_Lost
	goto_if_eq HAVE_TITLE, TRUE, JpMaster_EventScript_WonAgain
	mmsg T_GIVETITLE
	callnative JpMaster_SetBeaten
	call JpMaster_EventScript_EarnTitle
	mmsg T_ANOTHER
	callnative JpMaster_ResetMovementType
	release
	end

JpMaster_EventScript_WonAgain:
	mmsg T_AFTERWON
	release
	end

JpMaster_EventScript_Lost:
	mmsg T_LOST
	release
	end

JpMaster_EventScript_EarnTitle:
	message JpMaster_Text_EarnTitle
	waitmessage
	playfanfare MUS_LEVEL_UP
	waitfanfare
	waitbuttonpress
	return

@ Ditto, Articuno, Zapdos, Moltres, Mewtwo, Mew: a SCIENTIST who wants to see a Pokémon with 100 EVs
JpMaster_EventScript_NoBattle::
	lock
	faceplayer
	bufferspeciesname STR_VAR_1, TRAINER
	callnative JpMaster_Prepare
	goto_if_eq HAVE_TITLE, TRUE, JpMaster_EventScript_NoBattleHaveTitle
	mmsg T_INTRO
	msgbox JpMaster_Text_SeePowerfulMon
	callnative JpMaster_CheckSlot1
	goto_if_ne VAR_RESULT, TRUE, JpMaster_EventScript_ReleaseEnd
	callnative JpMaster_CheckSlot1EVs
	goto_if_ne VAR_RESULT, TRUE, JpMaster_EventScript_ReleaseEnd
	msgbox JpMaster_Text_ShowPowerfulMon
	callnative JpMaster_SetBeaten
	call JpMaster_EventScript_EarnTitle
	callnative JpMaster_ResetMovementType
	release
	end

JpMaster_EventScript_NoBattleHaveTitle:
	msgbox JpMaster_Text_HaveTitleNoBattle
	release
	end

JpMaster_EventScript_ReleaseEnd:
	release
	end

@ Pallet Town: the Master Trainer guide (FRLG+ PalletTown_EventScript_MasterYoungster)
JpMaster_EventScript_Guide::
	lock
	faceplayer
	msgbox JpMaster_Text_GuideIntro
	msgbox JpMaster_Text_GuideWho
	msgbox JpMaster_Text_GuideHow
	msgbox JpMaster_Text_GuideTitles
	release
	end

@ Celadon Condominiums 3F: the title giver (FRLG+ CeladonCity_Condominiums_3F_EventScript_TitleGiver)
JpMaster_EventScript_TitleGiver::
	lock
	faceplayer
	callnative JpMaster_HasAnyTitle
	goto_if_eq VAR_RESULT, FALSE, JpMaster_EventScript_TitleGiverNoTitles
	callnative JpMaster_BufferCurrentTitle
	goto_if_eq VAR_RESULT, 0, JpMaster_EventScript_TitleGiverNoneSelected
	msgbox JpMaster_Text_TitleGiverWelcomeTitle
	goto JpMaster_EventScript_TitleGiverMenu
JpMaster_EventScript_TitleGiverNoneSelected:
	msgbox JpMaster_Text_TitleGiverWelcomeNoTitle
JpMaster_EventScript_TitleGiverMenu:
	callnative JpMaster_TitleMenu
	waitstate
	switch VAR_RESULT
	case 0, JpMaster_EventScript_TitleGiverChoseNone
	case 152, JpMaster_EventScript_TitleGiverChoseGrand
	case 153, JpMaster_EventScript_TitleGiverPressedB
	callnative JpMaster_SetTitle
	bufferspeciesname STR_VAR_2, VAR_RESULT
	msgbox JpMaster_Text_TitleGiverChoseMon
	release
	end
JpMaster_EventScript_TitleGiverChoseNone:
	callnative JpMaster_SetTitle
	msgbox JpMaster_Text_TitleGiverChoseNone
	release
	end
JpMaster_EventScript_TitleGiverChoseGrand:
	callnative JpMaster_SetTitle
	msgbox JpMaster_Text_TitleGiverChoseGrand
	release
	end
JpMaster_EventScript_TitleGiverPressedB:
	msgbox JpMaster_Text_TitleGiverPressedB
	release
	end
JpMaster_EventScript_TitleGiverNoTitles:
	msgbox JpMaster_Text_TitleGiverNoTitles
	release
	end

@ Professor Oak: the superboss after all 151 titles (the lab's Oak object runs this first)
JpMaster_EventScript_Oak::
	goto_if_set FLAG_JP_OAK_WON_NOW, JpMaster_EventScript_OakJustWon
	callnative JpMaster_CanBattleOak
	goto_if_eq VAR_RESULT, TRUE, JpMaster_EventScript_OakAsk
	goto JpMaster_EventScript_OakOriginal
JpMaster_EventScript_OakAsk:
	lock
	faceplayer
	msgbox JpMaster_Text_OakAskBattle, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, JpMaster_EventScript_OakBattle
	msgbox JpMaster_Text_OakAtLeastLetMe
	release
JpMaster_EventScript_OakOriginal:
	.byte 0x05
JpMaster_OakOriginalScript::
	.4byte 0
JpMaster_EventScript_OakBattle:
	msgbox JpMaster_Text_OakStartBattle
	closemessage
	trainerbattle_no_intro JP_MASTER_BASE + 151, JpMaster_Text_OakDefeat
	setflag FLAG_JP_OAK_WON_NOW
	setvar TRAINER, 0
	callnative JpMaster_SetBeaten
	msgbox JpMaster_Text_OakWonBattle
	message JpMaster_Text_GrandMasterEarnTitle
	waitmessage
	playfanfare MUS_EVOLVED
	waitfanfare
	waitbuttonpress
	release
	end
JpMaster_EventScript_OakJustWon:
	lock
	faceplayer
	msgbox JpMaster_Text_OakJustWon
	release
	end

@ Pewter City / Route 2: FRLG+ opens a ledge once the Master Trainers are out
JpMaster_MapScript_PewterLedge::
	goto_if_unset FLAG_SYS_GAME_CLEAR, JpMaster_MapScript_PewterLedgeEnd
	setmetatile 28, 30, 0x28A, 1
JpMaster_MapScript_PewterLedgeEnd:
	.byte 0x05
JpMaster_PewterOnLoadNext::
	.4byte 0
JpMaster_MapScript_Route2Ledge::
	goto_if_unset FLAG_SYS_GAME_CLEAR, JpMaster_MapScript_Route2LedgeEnd
	setmetatile 2, 70, 0x2D7, 1
JpMaster_MapScript_Route2LedgeEnd:
	.byte 0x05
JpMaster_Route2OnLoadNext::
	.4byte 0

@ ------------------------------------------------------------------ texts
	.global gJpMasterTexts
	.align 2
gJpMasterTexts:
	.4byte JpMaster_Text_Intro0, JpMaster_Text_NoMon0, JpMaster_Text_Ask0, JpMaster_Text_AskT0, JpMaster_Text_Declined0, JpMaster_Text_Accepted0, JpMaster_Text_Lost0, JpMaster_Text_AfterWon0, JpMaster_Text_GiveTitle0, JpMaster_Text_Another0
	.4byte JpMaster_Text_Intro1, JpMaster_Text_NoMon1, JpMaster_Text_Ask1, JpMaster_Text_AskT1, JpMaster_Text_Declined1, JpMaster_Text_Accepted1, JpMaster_Text_Lost1, JpMaster_Text_AfterWon1, JpMaster_Text_GiveTitle1, JpMaster_Text_Another1
	.4byte JpMaster_Text_Intro2, JpMaster_Text_NoMon2, JpMaster_Text_Ask2, JpMaster_Text_AskT2, JpMaster_Text_Declined2, JpMaster_Text_Accepted2, JpMaster_Text_Lost2, JpMaster_Text_AfterWon2, JpMaster_Text_GiveTitle2, JpMaster_Text_Another2
	.4byte JpMaster_Text_Intro3, JpMaster_Text_NoMon3, JpMaster_Text_Ask3, JpMaster_Text_AskT3, JpMaster_Text_Declined3, JpMaster_Text_Accepted3, JpMaster_Text_Lost3, JpMaster_Text_AfterWon3, JpMaster_Text_GiveTitle3, JpMaster_Text_Another3
	.4byte JpMaster_Text_Intro4, JpMaster_Text_NoMon4, JpMaster_Text_Ask4, JpMaster_Text_AskT4, JpMaster_Text_Declined4, JpMaster_Text_Accepted4, JpMaster_Text_Lost4, JpMaster_Text_AfterWon4, JpMaster_Text_GiveTitle4, JpMaster_Text_Another4

@ --- 0: LASS / BEAUTY / SWIMMER
JpMaster_Text_Intro0:
	.string "わたしは {STR_VAR_1}マスター！\p"
	.string "めざすは さいきょうの\n"
	.string "{STR_VAR_1}よ！$"
JpMaster_Text_NoMon0:
	.string "わたしと しょうぶ したいなら\n"
	.string "{STR_VAR_1}を てもちの\l"
	.string "せんとうに してきてね！$"
JpMaster_Text_Ask0:
	.string "あら あなたの {STR_VAR_1}\n"
	.string "つよそうね！\p"
	.string "わたしの {STR_VAR_1}と\n"
	.string "しょうぶ してくれない？\l"
	.string "おねがーい！$"
JpMaster_Text_AskT0:
	.string "あら こんにちは！\n"
	.string "あなたの {STR_VAR_1}\l"
	.string "もっと つよく なった？\p"
	.string "わたしの {STR_VAR_1}と\n"
	.string "しょうぶ してくれない？\l"
	.string "おねがーい！$"
JpMaster_Text_Declined0:
	.string "ぶー！ わたしの {STR_VAR_1}を\n"
	.string "みせたかったのにー！$"
JpMaster_Text_Accepted0:
	.string "どっちの {STR_VAR_1}が つよいか\n"
	.string "しょうぶよ！$"
JpMaster_Text_Lost0:
	.string "うふふ！ やっぱり わたしの\n"
	.string "{STR_VAR_1}が いちばんね！$"
JpMaster_Text_AfterWon0:
	.string "うそ…… あなたの {STR_VAR_1}\n"
	.string "おもったより ずっと つよい！\p"
	.string "おたがい {STR_VAR_1}が\n"
	.string "だいすき なんだし\l"
	.string "また しょうぶ しましょ！$"
JpMaster_Text_GiveTitle0:
	.string "うそ…… あなたの {STR_VAR_1}\n"
	.string "おもったより ずっと つよい！\p"
	.string "あなたこそ {STR_VAR_1}マスターと\n"
	.string "よばれるのに ふさわしいわ！$"
JpMaster_Text_Another0:
	.string "おたがい {STR_VAR_1}が\n"
	.string "だいすき なんだし\l"
	.string "また しょうぶ しましょ！$"
JpMaster_Text_BattleLoss0:
	.string "その つよさ ほんものね！$"

@ --- 1: BIRD KEEPER / COOLTRAINER
JpMaster_Text_Intro1:
	.string "おれは {STR_VAR_1}マスター！\p"
	.string "さいきょうの {STR_VAR_1}を\n"
	.string "めざしているんだ！$"
JpMaster_Text_NoMon1:
	.string "おれと しょうぶ したいなら\n"
	.string "{STR_VAR_1}を てもちの\l"
	.string "せんとうに しておくんだな！$"
JpMaster_Text_Ask1:
	.string "おっ？ つよそうな\n"
	.string "{STR_VAR_1}を つれてるな！\p"
	.string "おれの {STR_VAR_1}と\n"
	.string "たたかわせて みないか？$"
JpMaster_Text_AskT1:
	.string "よう！ きみの {STR_VAR_1}\n"
	.string "また つよく なったかい？\p"
	.string "おれの {STR_VAR_1}と\n"
	.string "たたかわせて みないか？$"
JpMaster_Text_Declined1:
	.string "ざんねんだ！ おれの {STR_VAR_1}の\n"
	.string "すごさを みせられないとはな！$"
JpMaster_Text_Accepted1:
	.string "よし！ {STR_VAR_1}どうしの\n"
	.string "しょうぶ スタートだ！$"
JpMaster_Text_Lost1:
	.string "ははは！ やっぱり おれの\n"
	.string "{STR_VAR_1}が いちばんだ！$"
JpMaster_Text_AfterWon1:
	.string "しんじられない…… きみの\n"
	.string "{STR_VAR_1}…… つよすぎる！\p"
	.string "おたがい {STR_VAR_1}ずき\n"
	.string "また しょうぶ しような！$"
JpMaster_Text_GiveTitle1:
	.string "しんじられない…… きみの\n"
	.string "{STR_VAR_1}…… つよすぎる！\p"
	.string "{STR_VAR_1}マスターの なは\n"
	.string "きみにこそ ふさわしい！$"
JpMaster_Text_Another1:
	.string "おたがい {STR_VAR_1}ずき\n"
	.string "また しょうぶ しような！$"
JpMaster_Text_BattleLoss1:
	.string "その つよさ ほんものだな$"

@ --- 2: BLACK BELT / HIKER
JpMaster_Text_Intro2:
	.string "おれは {STR_VAR_1}マスター！\p"
	.string "おれの ねがいは ただひとつ\n"
	.string "さいきょうの {STR_VAR_1}を\l"
	.string "みつけることだ！$"
JpMaster_Text_NoMon2:
	.string "おれと しょうぶ したければ\n"
	.string "{STR_VAR_1}を てもちの\l"
	.string "せんとうに おくんだ！$"
JpMaster_Text_Ask2:
	.string "むむ？ おまえの {STR_VAR_1}\n"
	.string "なかなか つよそうだな！\p"
	.string "おれの {STR_VAR_1}と\n"
	.string "たたかわせて みないか？$"
JpMaster_Text_AskT2:
	.string "おお おまえか！\n"
	.string "おまえの {STR_VAR_1}は げんきか？\p"
	.string "おれの {STR_VAR_1}と\n"
	.string "たたかわせて みないか？$"
JpMaster_Text_Declined2:
	.string "ふむ…… おれの {STR_VAR_1}に\n"
	.string "おそれを なしたか？$"
JpMaster_Text_Accepted2:
	.string "いくぞ {STR_VAR_1}！\n"
	.string "せいせいどうどう しょうぶだ！$"
JpMaster_Text_Lost2:
	.string "がっはっは！ やはり おれの\n"
	.string "{STR_VAR_1}が いちばんだ！$"
JpMaster_Text_AfterWon2:
	.string "ば ばかな……！ おまえの\n"
	.string "{STR_VAR_1}は いままで みた\l"
	.string "どの {STR_VAR_1}より つよい！\p"
	.string "おなじ {STR_VAR_1}ずき どうし\n"
	.string "かぞくも どうぜんだ！\l"
	.string "また しょうぶ しようぜ！$"
JpMaster_Text_GiveTitle2:
	.string "ば ばかな……！ おまえの\n"
	.string "{STR_VAR_1}は いままで みた\l"
	.string "どの {STR_VAR_1}より つよい！\p"
	.string "おまえこそ {STR_VAR_1}マスターの\n"
	.string "なに ふさわしい！$"
JpMaster_Text_Another2:
	.string "おなじ {STR_VAR_1}ずき どうし\n"
	.string "かぞくも どうぜんだ！\l"
	.string "また しょうぶ しようぜ！$"
JpMaster_Text_BattleLoss2:
	.string "その つよさ ほんものだ！$"

@ --- 3: BUG CATCHER / YOUNGSTER
JpMaster_Text_Intro3:
	.string "ぼくは {STR_VAR_1}マスター！\n"
	.string "さいきょうの {STR_VAR_1}を\l"
	.string "さがしてるんだ！$"
JpMaster_Text_NoMon3:
	.string "ぼくと しょうぶ したいなら\n"
	.string "{STR_VAR_1}を てもちの\l"
	.string "せんとうに してよね！$"
JpMaster_Text_Ask3:
	.string "ねえねえ きみ つよい\n"
	.string "{STR_VAR_1}を もってるでしょ？\p"
	.string "ぼくの {STR_VAR_1}と\n"
	.string "たたかわせてよ！$"
JpMaster_Text_AskT3:
	.string "やあ げんき？ いまも\n"
	.string "{STR_VAR_1}を そだててるんでしょ！\p"
	.string "ぼくの {STR_VAR_1}と\n"
	.string "たたかわせてよ！$"
JpMaster_Text_Declined3:
	.string "ちぇっ！ きみの {STR_VAR_1}が\n"
	.string "たたかう ところ みたかったのに……$"
JpMaster_Text_Accepted3:
	.string "どっちの {STR_VAR_1}が つよいか\n"
	.string "しょうぶだ！$"
JpMaster_Text_Lost3:
	.string "やったー！ やっぱり ぼくの\n"
	.string "{STR_VAR_1}が いちばんだ！$"
JpMaster_Text_AfterWon3:
	.string "ええー！ きみの {STR_VAR_1}\n"
	.string "つよすぎるよ！\p"
	.string "おなじ {STR_VAR_1}ファンとして\n"
	.string "また しょうぶ したいな！$"
JpMaster_Text_GiveTitle3:
	.string "ええー！ きみの {STR_VAR_1}\n"
	.string "つよすぎるよ！\p"
	.string "きみこそ {STR_VAR_1}マスターだ！$"
JpMaster_Text_Another3:
	.string "おなじ {STR_VAR_1}ファンとして\n"
	.string "また しょうぶ したいな！$"
JpMaster_Text_BattleLoss3:
	.string "その つよさ ほんものだ！$"

@ --- 4: PSYCHIC / SCIENTIST
JpMaster_Text_Intro4:
	.string "わたしは {STR_VAR_1}マスター\n"
	.string "さいきょうの {STR_VAR_1}を\l"
	.string "もとめている$"
JpMaster_Text_NoMon4:
	.string "わたしと たたかいたいなら\n"
	.string "{STR_VAR_1}を てもちの\l"
	.string "せんとうに おきなさい$"
JpMaster_Text_Ask4:
	.string "ほう？ きみは じつに\n"
	.string "つよそうな {STR_VAR_1}を\l"
	.string "つれているね……\p"
	.string "わたしの {STR_VAR_1}と\n"
	.string "たたかって みないかね？$"
JpMaster_Text_AskT4:
	.string "やあ また あえたね\n"
	.string "きみの {STR_VAR_1}は げんきかね？\p"
	.string "わたしの {STR_VAR_1}と\n"
	.string "たたかって みないかね？$"
JpMaster_Text_Declined4:
	.string "わたしの {STR_VAR_1}の ちからを\n"
	.string "みせられないとは ざんねんだ$"
JpMaster_Text_Accepted4:
	.string "では かくごは いいかね？\n"
	.string "ゆけ {STR_VAR_1}！$"
JpMaster_Text_Lost4:
	.string "ふふふ…… やはり わたしの\n"
	.string "{STR_VAR_1}が もっとも つよい$"
JpMaster_Text_AfterWon4:
	.string "ばかな…… きみの {STR_VAR_1}は\n"
	.string "つよすぎる！\p"
	.string "{STR_VAR_1}を あいする もの どうし\n"
	.string "また いつか たたかおう！$"
JpMaster_Text_GiveTitle4:
	.string "ばかな…… きみの {STR_VAR_1}は\n"
	.string "つよすぎる！\p"
	.string "きみこそ {STR_VAR_1}マスターの\n"
	.string "しょうごうに ふさわしい！$"
JpMaster_Text_Another4:
	.string "{STR_VAR_1}を あいする もの どうし\n"
	.string "また いつか たたかおう！$"
JpMaster_Text_BattleLoss4:
	.string "それこそ しんの つよさだ$"

JpMaster_Text_EarnTitle:
	.string "{PLAYER}は {STR_VAR_1}マスターの\n"
	.string "しょうごうを てに いれた！$"

JpMaster_Text_SeePowerfulMon:
	.string "いちどで いいから ほんとうに\n"
	.string "つよい {STR_VAR_1}を みてみたい$"
JpMaster_Text_ShowPowerfulMon:
	.string "おや これは……\n"
	.string "その {STR_VAR_1}！\p"
	.string "なにか とくべつな ものを\n"
	.string "かんじる！\p"
	.string "たたずまい からして\n"
	.string "つよさが あふれでている……\l"
	.string "すばらしい！\p"
	.string "ありがとう……\n"
	.string "じつに みごとな ポケモンを\l"
	.string "みせて もらった\p"
	.string "きみこそ {STR_VAR_1}マスターと\n"
	.string "よばれるに ふさわしい！$"
JpMaster_Text_HaveTitleNoBattle:
	.string "やあ また あえたね\n"
	.string "きみの {STR_VAR_1}は げんきかね？$"

JpMaster_Text_GuideIntro:
	.string "チャンピオンに なった きみに\n"
	.string "おしらせ だよ！\p"
	.string "カントーの あちこちに\n"
	.string "マスタートレーナーが\l"
	.string "あらわれたんだ！$"
JpMaster_Text_GuideWho:
	.string "マスタートレーナーは それぞれ\n"
	.string "1しゅるいの ポケモンだけを\l"
	.string "そだてている トレーナーなんだ\p"
	.string "いつも てを ふって しょうぶを\n"
	.string "まっているから すぐに\l"
	.string "みつかると おもうよ$"
JpMaster_Text_GuideHow:
	.string "あいてと おなじ しゅるいの\n"
	.string "ポケモンを てもちの せんとうに\l"
	.string "していれば 1たい1で\l"
	.string "しょうぶ できるんだ\p"
	.string "おたがい どうぐは つかえないから\n"
	.string "うでだけが たよりの しょうぶさ！\p"
	.string "かてば しょうごうが もらえるよ$"
JpMaster_Text_GuideTitles:
	.string "しょうごうは タマムシシティの\n"
	.string "ゲームかいしゃで かえられるよ\p"
	.string "がんばってね！$"

JpMaster_Text_TitleGiverNoTitles:
	.string "ようこそ！\p"
	.string "なんの はなしか わからない\n"
	.string "かもしれないけど\l"
	.string "しょうごうを てに いれたら\l"
	.string "また きてね！$"
JpMaster_Text_TitleGiverWelcomeNoTitle:
	.string "ようこそ！\p"
	.string "しょうごうで よんで ほしい？$"
JpMaster_Text_TitleGiverWelcomeTitle:
	.string "ようこそ {STR_VAR_2}マスター！\p"
	.string "ちがう しょうごうで\n"
	.string "よんで ほしい？$"
JpMaster_Text_TitleGiverChoseNone:
	.string "しょうごうは いらないの？\n"
	.string "きみには ひつよう ないかもね！$"
JpMaster_Text_TitleGiverChoseGrand:
	.string "よっ グランドマスター！\n"
	.string "きみに ぴったりの しょうごうだね$"
JpMaster_Text_TitleGiverPressedB:
	.string "しょうごうは かえないの？\n"
	.string "いまの しょうごうが\l"
	.string "よっぽど きにいってるんだね！$"
JpMaster_Text_TitleGiverChoseMon:
	.string "よっ {STR_VAR_2}マスター！\n"
	.string "きみに ぴったりの しょうごうだね$"

JpMaster_Text_OakAskBattle:
	.string "おお {PLAYER}！\n"
	.string "ひさしぶり じゃな\l"
	.string "ずいぶん たくましく なったのう\p"
	.string "カントーの マスタートレーナーを\n"
	.string "ぜんいん たおしたそうじゃな\l"
	.string "じつに すばらしい！\p"
	.string "ポケモンへの ひたむきさ\n"
	.string "しんらい そして あいじょう……\l"
	.string "まったく たいしたものじゃ！\p"
	.string "わしも しばらく しょうぶを\n"
	.string "して おらんでな……\p"
	.string "わしと むかしからの なかまたちと\n"
	.string "ひとつ しょうぶ してみんか？$"
JpMaster_Text_OakAtLeastLetMe:
	.string "そうか ざんねんじゃのう$"
JpMaster_Text_OakStartBattle:
	.string "けいけん ゆたかな わしの\n"
	.string "ポケモンたちに どこまで\l"
	.string "やれるか みせて もらおう！$"
JpMaster_Text_OakDefeat:
	.string "みごとじゃ {PLAYER}！\n"
	.string "きみも ポケモンも すばらしい\l"
	.string "わしの めに くるいは なかった$"
JpMaster_Text_OakWonBattle:
	.string "{PLAYER}……\p"
	.string "きみは まず カントーの\n"
	.string "すべての ポケモンを\l"
	.string "ずかんに とうろく した……\p"
	.string "そして すべての ポケモンを\n"
	.string "そだてあげ しょうぶで\l"
	.string "その うでまえを しめした……\p"
	.string "わしは ながねんの けいけんと\n"
	.string "ふるい なかまたちで\l"
	.string "きみに かてると おもったが……\p"
	.string "……もう ポケモンの ちからを\n"
	.string "ひきだす ことに かけては\l"
	.string "きみの ほうが うえかも しれんな\p"
	.string "いますぐ ポケモンはかせに\n"
	.string "なれるほどじゃ！\p"
	.string "じゃが きみは まだまだ\n"
	.string "つよく なりたいんじゃろう\p"
	.string "その すばらしい せいかに\n"
	.string "グランドマスターの しょうごうを\l"
	.string "おくろう！\p"
	.string "おめでとう {PLAYER}！$"
JpMaster_Text_GrandMasterEarnTitle:
	.string "{PLAYER}は グランドマスターの\n"
	.string "しょうごうを てに いれた！$"
JpMaster_Text_OakJustWon:
	.string "しばらくは もう\n"
	.string "しょうぶは せんよ\p"
	.string "わしと ポケモンたちが\n"
	.string "げんえきを しりぞいたのには\l"
	.string "わけが あるんじゃ$"
