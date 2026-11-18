#include "constants/global.h"
#include "constants/flags.h"
#include "constants/vars.h"
#include "constants/songs.h"
#include "constants/items.h"
#include "constants/species.h"
#include "constants/event_objects.h"
#include "constants/event_object_movement.h"
#include "constants/map_scripts.h"
#include "constants/battle.h"
#include "constants/game_stat.h"
#include "constants/field_weather.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.set FALSE, 0
	.set TRUE, 1
	.set YES, 1
	.set NO, 0

@ FRLG+ RS Battle Tower (JP port; maps built by tools/bt_patch.py, logic in src/hooks/hk_battle_tower.c)
	.set MAP_JP_BT_OUTSIDE,  (42 << 8) | 1
	.set MAP_JP_BT_LOBBY,    (42 << 8) | 2
	.set MAP_JP_BT_ELEVATOR, (42 << 8) | 3
	.set MAP_JP_BT_CORRIDOR, (42 << 8) | 4
	.set MAP_JP_BT_ROOM,     (42 << 8) | 5
	.set FLAG_JP_DEFEATED_SUDOWOODO, 0x0EB
	.set FLAG_SYS_CTRL_OBJ_DELETE, 0x82A
	.set FLAG_SYS_IS_LINKING, 0x82B
	.set FLAG_JP_CAUGHT_SUDOWOODO,   0x0EC
	.set FLAG_JP_HIDE_SUDOWOODO,     0x0ED
	.set FLAG_JP_HIDE_SCOTT,         0x0EE
	.set FLAG_JP_HIDE_BT_OPPONENT,   0x0EF
	.set LOCALID_SUDOWOODO, 7
	.set LOCALID_SCOTT, 5
	.set JP_MC_BT_LEVELS, 64
	.set JP_MC_FERRY_BT, 65
	.set MULTICHOICE_CHALLENGE_INFO_EXIT, 19
	.set SEAGALLOP_VERMILION_CITY, 0
	.set SEAGALLOP_NAVEL_ROCK, 9
	.set SEAGALLOP_BATTLE_TOWER, 12
	.set SPECIAL_HealPlayerParty, 0
	.set SPECIAL_SavePlayerParty, 39
	.set SPECIAL_LoadPlayerParty, 40
	.set SPECIAL_GetBattleOutcome, 180
	.set SPECIAL_BattleTowerMapScript2, 231
	.set SPECIAL_ChooseNextBattleTowerTrainer, 232
	.set SPECIAL_CheckPartyBattleTowerBanlist, 233
	.set SPECIAL_PrintBattleTowerTrainerGreeting, 234
	.set SPECIAL_StartSpecialBattle, 236
	.set SPECIAL_SetBattleTowerProperty, 237
	.set SPECIAL_BattleTowerUtil, 238
	.set SPECIAL_SetBattleTowerParty, 239
	.set SPECIAL_SaveBattleTowerProgress, 240
	.set SPECIAL_BattleTower_SoftReset, 241
	.set SPECIAL_DetermineBattleTowerPrize, 242
	.set SPECIAL_GiveBattleTowerPrize, 243
	.set SPECIAL_AwardBattleTowerRibbons, 244
	.set SPECIAL_ChooseBattleTowerPlayerParty, 245
	.set SPECIAL_AnimateElevator, 273
	.set SPECIAL_DoSeagallopFerryScene, 379
	.set SPECIAL_QuestLog_CutRecording, 392
	.set SPECIAL_Field_AskSaveTheGame, 93

	.section .rodata
	.align 2

@ ------------------------------------------------------------------ Vermilion City: the ferry sailor (Rainbow Pass)
JpBT_EventScript_FerryRainbow::
	message JpBT_Text_FerryWhere
	waitmessage
	multichoice 17, 6, JP_MC_FERRY_BT, FALSE
	switch VAR_RESULT
	case 0, JpBT_EventScript_FerrySevii
	case 1, JpBT_EventScript_SailToBattleTower
	release
	end
JpBT_EventScript_FerrySevii:
	.byte 0x05
JpBT_FerryRainbowOriginal::
	.4byte 0
JpBT_EventScript_SailToBattleTower:
	msgbox JpBT_Text_FerryToBattleTower
	setvar VAR_0x8004, SEAGALLOP_VERMILION_CITY
	setvar VAR_0x8006, SEAGALLOP_BATTLE_TOWER
	closemessage
	delay 20
	special QuestLog_CutRecording
	fadescreen FADE_TO_BLACK
	special DoSeagallopFerryScene
	waitstate
	end

@ ------------------------------------------------------------------ outside
JpBT_Outside_MapScripts::
	map_script MAP_SCRIPT_ON_RESUME, JpBT_Outside_OnResume
	map_script MAP_SCRIPT_ON_TRANSITION, JpBT_Outside_OnTransition
	.byte 0

JpBT_Outside_OnResume:
	call_if_set FLAG_SYS_CTRL_OBJ_DELETE, JpBT_Outside_TryRemoveSudowoodo
	end
JpBT_Outside_TryRemoveSudowoodo:
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, JpBT_Return
	removeobject VAR_LAST_TALKED
	return
JpBT_Return:
	return

JpBT_Outside_OnTransition:
	setflag FLAG_JP_HIDE_SUDOWOODO
	call_if_unset FLAG_JP_DEFEATED_SUDOWOODO, JpBT_Outside_ShowSudowoodo
	end
JpBT_Outside_ShowSudowoodo:
	goto_if_set FLAG_JP_CAUGHT_SUDOWOODO, JpBT_Return
	clearflag FLAG_JP_HIDE_SUDOWOODO
	return

JpBT_Outside_EventScript_Sign::
	msgbox JpBT_Text_OutsideSign, MSGBOX_SIGN
	end
JpBT_Outside_EventScript_BugCatcher::
	msgbox JpBT_Text_OutsideBugCatcher, MSGBOX_NPC
	end
JpBT_Outside_EventScript_Cooltrainer::
	msgbox JpBT_Text_OutsideCooltrainer, MSGBOX_NPC
	end
JpBT_Outside_EventScript_Boy::
	msgbox JpBT_Text_OutsideBoy, MSGBOX_NPC
	end

JpBT_Outside_EventScript_OldWoman::
	lock
	faceplayer
	goto_if_set FLAG_JP_DEFEATED_SUDOWOODO, JpBT_Outside_OldWomanGone
	goto_if_set FLAG_JP_CAUGHT_SUDOWOODO, JpBT_Outside_OldWomanGone
	msgbox JpBT_Text_OddTreeWiggles
	release
	end
JpBT_Outside_OldWomanGone:
	msgbox JpBT_Text_OnceAnOddTree
	release
	end

JpBT_Outside_EventScript_Sudowoodo::
	lock
	faceplayer
	waitse
	playse SE_PIN
	applymovement LOCALID_SUDOWOODO, JpBT_Movement_SudowoodoShake
	waitmovement 0
	checkitem ITEM_FRESH_WATER, 1
	goto_if_eq VAR_RESULT, TRUE, JpBT_Outside_AskWaterSudowoodo
	release
	end
JpBT_Outside_AskWaterSudowoodo:
	msgbox JpBT_Text_UseFreshWater, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, JpBT_Outside_WaterSudowoodo
	release
	end
JpBT_Outside_WaterSudowoodo:
	removeitem ITEM_FRESH_WATER, 1
	playse SE_PIN
	applymovement LOCALID_SUDOWOODO, JpBT_Movement_SudowoodoShakeAngry
	waitmovement 0
	applymovement LOCALID_SUDOWOODO, JpBT_Movement_SudowoodoShakeAngry
	waitmovement 0
	applymovement LOCALID_SUDOWOODO, JpBT_Movement_SudowoodoShakeAngry
	waitmovement 0
	msgbox JpBT_Text_SudowoodoAttacked
	closemessage
	waitse
	playmoncry SPECIES_SUDOWOODO, 2
	delay 40
	waitmoncry
	setvar VAR_LAST_TALKED, LOCALID_SUDOWOODO
	setwildbattle SPECIES_SUDOWOODO, 40, ITEM_NONE
	setflag FLAG_SYS_CTRL_OBJ_DELETE
	dowildbattle
	clearflag FLAG_SYS_CTRL_OBJ_DELETE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, JpBT_Outside_DefeatedSudowoodo
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, JpBT_Outside_SudowoodoFled
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, JpBT_Outside_SudowoodoFled
	setflag FLAG_JP_CAUGHT_SUDOWOODO
	release
	end
JpBT_Outside_DefeatedSudowoodo:
	setflag FLAG_JP_DEFEATED_SUDOWOODO
JpBT_Outside_SudowoodoFled:
	fadescreen FADE_TO_BLACK
	removeobject VAR_LAST_TALKED
	fadescreen FADE_FROM_BLACK
	msgbox JpBT_Text_WeirdTreeFled
	release
	end

JpBT_Movement_SudowoodoShake:
	face_right
	delay_8
	face_down
	delay_8
	face_left
	delay_8
	face_down
	delay_8
	face_right
	delay_8
	face_down
	delay_8
	face_left
	delay_8
	face_down
	step_end
JpBT_Movement_SudowoodoShakeAngry:
	face_right
	delay_2
	face_down
	delay_2
	face_left
	delay_2
	face_down
	delay_2
	face_right
	delay_2
	face_down
	delay_2
	face_left
	delay_2
	face_down
	step_end

@ the sailor at the dock takes the player back to Vermilion
JpBT_Outside_EventScript_Sailor::
	lock
	faceplayer
	msgbox JpBT_Text_SailorBackToVermilion, MSGBOX_YESNO
	goto_if_ne VAR_RESULT, YES, JpBT_Outside_SailorNo
	setvar VAR_0x8004, SEAGALLOP_BATTLE_TOWER
	setvar VAR_0x8006, SEAGALLOP_VERMILION_CITY
	closemessage
	delay 20
	special QuestLog_CutRecording
	fadescreen FADE_TO_BLACK
	special DoSeagallopFerryScene
	waitstate
	end
JpBT_Outside_SailorNo:
	release
	end

@ ------------------------------------------------------------------ lobby
JpBT_Lobby_MapScripts::
	map_script MAP_SCRIPT_ON_RESUME, JpBT_Lobby_OnResume
	map_script MAP_SCRIPT_ON_FRAME_TABLE, JpBT_Lobby_OnFrame
	map_script MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE, JpBT_Lobby_OnWarp
	.byte 0

JpBT_Lobby_OnResume:
	call JpBT_Lobby_Setup
	end

JpBT_Lobby_Setup:
	setvar VAR_0x8004, 10
	special SetBattleTowerProperty
	goto_if_set FLAG_TEMP_1, JpBT_Lobby_ReleaseEnd
	checkitem ITEM_AURORA_TICKET, 1
	goto_if_eq VAR_RESULT, TRUE, JpBT_Lobby_HideScott
	callnative GetBestBattleTowerStreakToVar0x8007
	goto_if_lt VAR_0x8007, 28, JpBT_Lobby_HideScott
	clearflag FLAG_JP_HIDE_SCOTT
	callnative TryInitBattleTowerAwardManObjectEvent
	return
JpBT_Lobby_HideScott:
	setflag FLAG_JP_HIDE_SCOTT
	return

JpBT_Lobby_OnWarp:
	map_script_2 VAR_TEMP_1, 0, JpBT_Lobby_TurnPlayer
	.2byte 0
JpBT_Lobby_TurnPlayer:
	setvar VAR_TEMP_1, 1
	turnobject OBJ_EVENT_ID_PLAYER, DIR_NORTH
	end

JpBT_Lobby_OnFrame:
	map_script_2 VAR_TEMP_0, 0, JpBT_Lobby_State0
	map_script_2 VAR_TEMP_0, 1, JpBT_Lobby_DidntSave
	map_script_2 VAR_TEMP_0, 2, JpBT_Lobby_Beat7
	map_script_2 VAR_TEMP_0, 3, JpBT_Lobby_Lost
	map_script_2 VAR_TEMP_0, 4, JpBT_Lobby_Resume
	.2byte 0

JpBT_Lobby_State0:
	special BattleTowerMapScript2
	end

JpBT_Lobby_DidntSave:
	lock
	faceplayer
	textcolor 1
	clearflag FLAG_SYS_IS_LINKING
	msgbox JpBT_Text_DidntSave
	closemessage
	setvar VAR_TEMP_0, 5
	release
	end

JpBT_Lobby_Beat7:
	lock
	faceplayer
	clearflag FLAG_SYS_IS_LINKING
	textcolor 1
	message JpBT_Text_Beat7
	waitmessage
	setvar VAR_0x8004, 0
	special BattleTowerUtil
	goto_if_eq VAR_RESULT, 6, JpBT_Lobby_Beat7Save
	special AwardBattleTowerRibbons
	goto_if_eq VAR_RESULT, 0, JpBT_Lobby_Beat7Save
	message JpBT_Text_Ribbons
	waitmessage
	playfanfare MUS_OBTAIN_ITEM
	waitfanfare
	msgbox JpBT_Text_RibbonsPut
JpBT_Lobby_Beat7Save:
	setvar VAR_0x8004, 8
	special BattleTowerUtil
	goto_if_eq VAR_RESULT, 1, JpBT_Lobby_Prize
	message JpBT_Text_RecordSaved
	waitmessage
	setvar VAR_0x8004, 13
	special SetBattleTowerProperty
	special DetermineBattleTowerPrize
	setvar VAR_0x8004, 3
	special SaveBattleTowerProgress
	playse SE_SAVE
	waitse
JpBT_Lobby_Prize:
	setvar VAR_0x8004, 0
	setvar VAR_0x8005, 3
	special SetBattleTowerProperty
	message JpBT_Text_Prize
	waitmessage
	special GiveBattleTowerPrize
	goto_if_eq VAR_RESULT, 0, JpBT_Lobby_BagFull
	textcolor 3
	message JpBT_Text_ReceivedPrize
	waitmessage
	playfanfare MUS_OBTAIN_ITEM
	waitfanfare
	setvar VAR_0x8004, 9
	textcolor 1
	special BattleTowerUtil
	goto_if_ne VAR_RESULT, 49, JpBT_Lobby_LookingForward
	msgbox JpBT_Text_Next50th
JpBT_Lobby_LookingForward:
	msgbox JpBT_Text_LookingForward
	closemessage
	setvar VAR_TEMP_0, 5
	release
	end
JpBT_Lobby_BagFull:
	msgbox JpBT_Text_BagFull
	closemessage
	setvar VAR_TEMP_0, 5
	release
	end

JpBT_Lobby_Lost:
	lock
	faceplayer
	textcolor 1
	clearflag FLAG_SYS_IS_LINKING
	message JpBT_Text_ThanksForPlaying
	waitmessage
	message JpBT_Text_RecordSaved
	waitmessage
	setvar VAR_0x8004, 13
	special SetBattleTowerProperty
	setvar VAR_0x8004, 0
	special SaveBattleTowerProgress
	playse SE_SAVE
	waitse
	msgbox JpBT_Text_LookingForward
	closemessage
	setvar VAR_TEMP_0, 5
	release
	end

JpBT_Lobby_Resume:
	lock
	faceplayer
	textcolor 1
	message JpBT_Text_BeenWaiting
	waitmessage
	message JpBT_Text_WillSave
	waitmessage
	setvar VAR_0x8004, 1
	special SaveBattleTowerProgress
	playse SE_SAVE
	waitse
	setvar VAR_0x8004, 8
	setvar VAR_0x8005, 0
	special SetBattleTowerProperty
	setvar VAR_TEMP_0, 5
	special SavePlayerParty
	setflag FLAG_SYS_IS_LINKING
	callnative RecalculatePartyStats
	special SetBattleTowerParty
	msgbox JpBT_Text_DirectYou
	closemessage
	call JpBT_Lobby_WalkToElevator
	warp MAP_JP_BT_ELEVATOR, 255, 2, 6
	setvar VAR_TEMP_0, 0
	waitstate

JpBT_Lobby_EventScript_Receptionist::
	lock
	faceplayer
	setvar VAR_0x8004, 0
	special BattleTowerUtil
	goto_if_eq VAR_RESULT, 6, JpBT_Lobby_Beat7
	special SavePlayerParty
	msgbox JpBT_Text_Welcome
JpBT_Lobby_AskChallenge:
	message JpBT_Text_AskChallenge
	waitmessage
	multichoice 17, 6, MULTICHOICE_CHALLENGE_INFO_EXIT, FALSE
	switch VAR_RESULT
	case 0, JpBT_Lobby_Challenge
	case 1, JpBT_Lobby_Info
	goto JpBT_Lobby_Cancel

JpBT_Lobby_Challenge:
	message JpBT_Text_WhichLevel
	waitmessage
	multichoice 17, 6, JP_MC_BT_LEVELS, FALSE
	switch VAR_RESULT
	case 2, JpBT_Lobby_Cancel
	case 127, JpBT_Lobby_Cancel
	special CheckPartyBattleTowerBanlist
	goto_if_eq VAR_0x8004, 1, JpBT_Lobby_NotEligible
	setvar VAR_0x8004, 1
	copyvar VAR_0x8005, VAR_RESULT
	copyvar VAR_0x8006, VAR_RESULT
	special SetBattleTowerProperty
	msgbox JpBT_Text_SelectMons
	setflag FLAG_TEMP_1
	fadescreen FADE_TO_BLACK
	special ChooseBattleTowerPlayerParty
	waitstate
	clearflag FLAG_TEMP_1
	goto_if_eq VAR_RESULT, 0, JpBT_Lobby_CancelLoad
	msgbox JpBT_Text_MustSave, MSGBOX_YESNO
	goto_if_ne VAR_RESULT, YES, JpBT_Lobby_CancelLoad
	setvar VAR_0x8004, 5
	special SetBattleTowerProperty
	setvar VAR_TEMP_0, 0
	setvar VAR_0x8004, 11
	special SetBattleTowerProperty
	setvar VAR_0x8004, 0
	setvar VAR_0x8005, 1
	special SetBattleTowerProperty
	setvar VAR_0x8004, 8
	setvar VAR_0x8005, 0
	special SetBattleTowerProperty
	setdynamicwarp MAP_JP_BT_LOBBY, 255, 6, 6
	special LoadPlayerParty
	closemessage
	delay 2
	special Field_AskSaveTheGame
	waitstate
	setvar VAR_TEMP_0, 5
	goto_if_eq VAR_RESULT, 0, JpBT_Lobby_SaveFailed
	incrementgamestat GAME_STAT_ENTERED_BATTLE_TOWER
	special SavePlayerParty
	setflag FLAG_SYS_IS_LINKING
	callnative RecalculatePartyStats
	special SetBattleTowerParty
	msgbox JpBT_Text_DirectYou
	closemessage
	call JpBT_Lobby_WalkToElevator
	warp MAP_JP_BT_ELEVATOR, 255, 2, 6
	setvar VAR_TEMP_0, 0
	waitstate

JpBT_Lobby_Info:
	msgbox JpBT_Text_Info
	goto JpBT_Lobby_AskChallenge

JpBT_Lobby_NotEligible:
	textcolor 1
	goto_if_eq VAR_RESULT, 1, JpBT_Lobby_NotEligibleOpen
	msgbox JpBT_Text_NotEligible50
	goto JpBT_Lobby_ReleaseEnd
JpBT_Lobby_NotEligibleOpen:
	msgbox JpBT_Text_NotEligibleOpen
	goto JpBT_Lobby_ReleaseEnd

JpBT_Lobby_SaveFailed:
	setvar VAR_0x8004, 12
	special SetBattleTowerProperty
	goto JpBT_Lobby_Cancel
JpBT_Lobby_CancelLoad:
	special LoadPlayerParty
JpBT_Lobby_Cancel:
	msgbox JpBT_Text_LookingForward
	setvar VAR_0x8004, 11
	special SetBattleTowerProperty
JpBT_Lobby_ReleaseEnd:
	release
	end

JpBT_Lobby_WalkToElevator:
	applymovement 1, JpBT_Movement_Up3
	applymovement OBJ_EVENT_ID_PLAYER, JpBT_Movement_Up3
	waitmovement 0
	opendoor 6, 1
	waitdooranim
	applymovement 1, JpBT_Movement_UpVanish
	applymovement OBJ_EVENT_ID_PLAYER, JpBT_Movement_Up2Vanish
	waitmovement 0
	closedoor 6, 1
	waitdooranim
	return

JpBT_Movement_Up3:
	walk_up
	walk_up
	walk_up
	step_end
JpBT_Movement_UpVanish:
	walk_up
	set_invisible
	step_end
JpBT_Movement_Up2Vanish:
	walk_up
	walk_up
	set_invisible
	step_end

JpBT_Lobby_EventScript_Worker::
	msgbox JpBT_Text_LobbyWorker, MSGBOX_NPC
	end
JpBT_Lobby_EventScript_Cooltrainer::
	msgbox JpBT_Text_LobbyCooltrainer, MSGBOX_NPC
	end
JpBT_Lobby_EventScript_Boy::
	msgbox JpBT_Text_LobbyBoy, MSGBOX_NPC
	end
JpBT_Lobby_EventScript_Records::
	lockall
	callnative JpBT_ShowRecords
	waitbuttonpress
	callnative JpBT_RemoveRecords
	releaseall
	end

JpBT_Lobby_EventScript_Scott::
	lock
	faceplayer
	checkitem ITEM_AURORA_TICKET, 1
	goto_if_eq VAR_RESULT, TRUE, JpBT_Lobby_ScottGave
	msgbox JpBT_Text_Scott28Wins
	giveitem ITEM_AURORA_TICKET
	setflag FLAG_RECEIVED_AURORA_TICKET
	setflag FLAG_ENABLE_SHIP_BIRTH_ISLAND
	msgbox JpBT_Text_ScottExplainAurora
	release
	end
JpBT_Lobby_ScottGave:
	msgbox JpBT_Text_ScottGaveAurora
	release
	end

@ ------------------------------------------------------------------ elevator
JpBT_Elevator_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, JpBT_Elevator_OnFrame
	map_script MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE, JpBT_Elevator_OnWarp
	.byte 0
JpBT_Elevator_OnFrame:
	map_script_2 VAR_TEMP_0, 0, JpBT_Elevator_Ride
	.2byte 0
JpBT_Elevator_Ride:
	setvar VAR_TEMP_0, 1
	applymovement 1, JpBT_Movement_ElevAttendantIn
	applymovement OBJ_EVENT_ID_PLAYER, JpBT_Movement_ElevPlayerIn
	waitmovement 0
	special AnimateElevator
	waitstate
	delay 64
	applymovement 1, JpBT_Movement_ElevAttendantOut
	applymovement OBJ_EVENT_ID_PLAYER, JpBT_Movement_ElevPlayerOut
	waitmovement 0
	setvar VAR_TEMP_0, 0
	warp MAP_JP_BT_CORRIDOR, 255, 8, 1
	waitstate
	end
JpBT_Elevator_OnWarp:
	map_script_2 VAR_TEMP_1, 0, JpBT_Elevator_TurnPlayer
	.2byte 0
JpBT_Elevator_TurnPlayer:
	setvar VAR_TEMP_1, 1
	turnobject OBJ_EVENT_ID_PLAYER, DIR_NORTH
	end
JpBT_Movement_ElevAttendantIn:
	walk_up
	walk_right
	face_down
	step_end
JpBT_Movement_ElevPlayerIn:
	walk_up
	walk_up
	face_down
	step_end
JpBT_Movement_ElevAttendantOut:
	walk_down
	walk_left
	walk_down
	set_invisible
	step_end
JpBT_Movement_ElevPlayerOut:
	delay_16
	delay_16
	walk_down
	walk_down
	step_end

@ ------------------------------------------------------------------ corridor
JpBT_Corridor_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, JpBT_Corridor_OnLoad
	map_script MAP_SCRIPT_ON_FRAME_TABLE, JpBT_Corridor_OnFrame
	.byte 0
JpBT_Corridor_OnLoad:
	goto_if_eq VAR_0x8006, 1, JpBT_Corridor_OpenFar
	setmetatile 12, 0, 0x287, 0
	setmetatile 12, 1, 0x28F, 0
	end
JpBT_Corridor_OpenFar:
	setmetatile 15, 0, 0x287, 0
	setmetatile 15, 1, 0x28F, 0
	end
JpBT_Corridor_OnFrame:
	map_script_2 VAR_TEMP_0, 0, JpBT_Corridor_Walk
	.2byte 0
JpBT_Corridor_Walk:
	setvar VAR_TEMP_0, 1
	goto_if_eq VAR_0x8006, 1, JpBT_Corridor_WalkFar
	applymovement 1, JpBT_Movement_CorrNear
	applymovement OBJ_EVENT_ID_PLAYER, JpBT_Movement_CorrNearPlayer
	waitmovement 0
	goto JpBT_Corridor_Enter
JpBT_Corridor_WalkFar:
	applymovement 1, JpBT_Movement_CorrFar
	applymovement OBJ_EVENT_ID_PLAYER, JpBT_Movement_CorrFarPlayer
	waitmovement 0
JpBT_Corridor_Enter:
	setvar VAR_TEMP_0, 0
	warp MAP_JP_BT_ROOM, 255, 4, 8
	waitstate
	end
JpBT_Movement_CorrFarPlayer:
	walk_right
JpBT_Movement_CorrFar:
	walk_right
	walk_right
JpBT_Movement_CorrNearPlayer:
	walk_right
JpBT_Movement_CorrNear:
	walk_right
	walk_right
	walk_right
	walk_up
	set_invisible
	step_end

@ ------------------------------------------------------------------ battle room
JpBT_Room_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, JpBT_Room_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, JpBT_Room_OnFrame
	.byte 0
JpBT_Room_OnTransition:
	setflag FLAG_JP_HIDE_BT_OPPONENT
	end
JpBT_Room_OnFrame:
	map_script_2 VAR_TEMP_0, 0, JpBT_Room_Enter
	.2byte 0
JpBT_Room_Enter:
	setvar VAR_TEMP_0, 1
	applymovement OBJ_EVENT_ID_PLAYER, JpBT_Movement_RoomPlayerIn
	waitmovement 0
JpBT_Room_NextOpponent:
	special ChooseNextBattleTowerTrainer
	addobject 1
	applymovement 1, JpBT_Movement_RoomOpponentIn
	waitmovement 0
	call_if_eq VAR_LAST_TALKED, 0, JpBT_Room_TextcolorMale
	call_if_eq VAR_LAST_TALKED, 1, JpBT_Room_TextcolorFemale
	special PrintBattleTowerTrainerGreeting
	msgbox gStringVar4
	waitmessage
	closemessage
	special HealPlayerParty
	setvar VAR_0x8004, 0
	setvar VAR_0x8005, 0
	special StartSpecialBattle
	waitstate
	switch VAR_RESULT
	case 1, JpBT_Room_Won
	special LoadPlayerParty
	setvar VAR_0x8004, 0
	setvar VAR_0x8005, 5
	special SetBattleTowerProperty
	setvar VAR_0x8004, 14
	special SetBattleTowerProperty
	setvar VAR_0x8004, 3
	warp MAP_JP_BT_LOBBY, 255, 6, 6
	waitstate

JpBT_Room_Won:
	setvar VAR_0x8004, 6
	special SetBattleTowerProperty
	switch VAR_RESULT
	case 8, JpBT_Room_Beat7
	applymovement 1, JpBT_Movement_RoomOpponentOut
	waitmovement 0
	removeobject 1
	applymovement 2, JpBT_Movement_RoomAttendantIn
	waitmovement 0
	applymovement OBJ_EVENT_ID_PLAYER, JpBT_Movement_FaceDown
	waitmovement 0
	textcolor 1
	msgbox JpBT_Text_WillRestore
	special LoadPlayerParty
	special SavePlayerParty
	special SetBattleTowerParty
	playfanfare MUS_HEAL
	waitfanfare
	special HealPlayerParty
JpBT_Room_AskReady:
	textcolor 1
	msgbox JpBT_Text_AskReady, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, JpBT_Room_Continue
	msgbox JpBT_Text_AskSaveQuit, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, JpBT_Room_SaveQuit
	msgbox JpBT_Text_AskCancel, MSGBOX_YESNO
	goto_if_ne VAR_RESULT, YES, JpBT_Room_AskReady
	goto JpBT_Room_Retire
JpBT_Room_Continue:
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, JpBT_Movement_FaceRight
	waitmovement 0
	applymovement 2, JpBT_Movement_RoomAttendantOut
	waitmovement 0
	goto JpBT_Room_NextOpponent

JpBT_Room_Beat7:
	special LoadPlayerParty
	setvar VAR_0x8004, 0
	setvar VAR_0x8005, 4
	special SetBattleTowerProperty
	setvar VAR_0x8004, 2
	setvar VAR_0x8005, 1
	special SetBattleTowerProperty
	setvar VAR_0x8004, 7
	special SetBattleTowerProperty
	setvar VAR_0x8004, 14
	special SetBattleTowerProperty
	setvar VAR_0x8004, 3
	warp MAP_JP_BT_LOBBY, 255, 6, 6
	waitstate

JpBT_Room_SaveQuit:
	setvar VAR_0x8004, 2
	special SaveBattleTowerProgress
	textcolor 3
	message JpBT_Text_Saving
	delay 60
	waitmessage
	playse SE_SAVE
	waitse
	msgbox JpBT_Text_Saved
JpBT_Room_Retire:
	fadescreen FADE_TO_BLACK
	special BattleTower_SoftReset
	end

JpBT_Room_TextcolorMale:
	textcolor 0
	return
JpBT_Room_TextcolorFemale:
	textcolor 1
	return

JpBT_Movement_RoomPlayerIn:
	walk_up
	walk_up
	walk_up
	face_right
	step_end
JpBT_Movement_FaceDown:
	face_down
	step_end
JpBT_Movement_FaceRight:
	face_right
	step_end
JpBT_Movement_RoomOpponentIn:
	walk_down
	walk_down
	walk_down
	walk_down
	face_left
	step_end
JpBT_Movement_RoomOpponentOut:
	walk_up
	walk_up
	walk_up
	walk_up
	step_end
JpBT_Movement_RoomAttendantIn:
	walk_right
	walk_right
	walk_right
	walk_up
	step_end
JpBT_Movement_RoomAttendantOut:
	walk_down
	walk_left
	walk_left
	walk_left
	face_right
	step_end

@ ------------------------------------------------------------------ multichoice lists (sMultichoiceLists 64, 65)
	.global gJpBTMultichoiceLevels
	.align 2
gJpBTMultichoiceLevels:
	.4byte JpBT_Text_Lv50, 0, JpBT_Text_OpenLevel, 0, JpBT_Text_Quit, 0
	.global gJpBTMultichoiceFerry
gJpBTMultichoiceFerry:
	.4byte JpBT_Text_Sevii, 0, JpBT_Text_BattleTower, 0, JpBT_Text_Quit, 0
JpBT_Text_Lv50:
	.string "レベル50$"
JpBT_Text_OpenLevel:
	.string "オープンレベル$"
JpBT_Text_Quit:
	.string "やめる$"
JpBT_Text_Sevii:
	.string "ナナシマ$"
JpBT_Text_BattleTower::
	.string "バトルタワー$"

@ ------------------------------------------------------------------ texts
JpBT_Text_FerryWhere:
	.string "シーギャロップごうに\n"
	.string "ようこそ！\p"
	.string "どちらへ いかれますか？$"
JpBT_Text_FerryToBattleTower:
	.string "バトルタワー いきの\n"
	.string "シーギャロップ13ごう しゅっこう！$"
JpBT_Text_SailorBackToVermilion:
	.string "シーギャロップごうで\n"
	.string "クチバシティに もどりますか？$"

JpBT_Text_OutsideSign:
	.string "バトルタワー\n"
	.string "“めざせ さいきょう トレーナー！”$"
JpBT_Text_OutsideBugCatcher:
	.string "ここは バトルタワー\p"
	.string "トレーナーが じまんの ポケモンを\n"
	.string "つれてきて かちぬきせんで\l"
	.string "しょうぶ するんだ$"
JpBT_Text_OutsideCooltrainer:
	.string "35にん れんしょう するまでは\n"
	.string "ぜったい かえらないわ！$"
JpBT_Text_OutsideBoy:
	.string "うわあ…… つよそうな\n"
	.string "トレーナーが いっぱい……\p"
	.string "ぼくは まだまだ\n"
	.string "ちょうせん できないや……$"
JpBT_Text_OddTreeWiggles:
	.string "ちょいと そこの おかた\n"
	.string "めは いいほうかね？\p"
	.string "そこに へんな きが あってね\n"
	.string "わたしの めには\l"
	.string "うごいてる ように みえるんだよ$"
JpBT_Text_OnceAnOddTree:
	.string "ちょいと そこの おかた\n"
	.string "ものおぼえは いいほうかね？\p"
	.string "むかし ここに へんな きが\n"
	.string "あったような きが するんだよ$"
JpBT_Text_UseFreshWater:
	.string "へんな きだ\n"
	.string "おいしいみずを かけますか？$"
JpBT_Text_SudowoodoAttacked:
	.string "へんな きは おいしいみずが\n"
	.string "きらい みたいだ！\p"
	.string "へんな きが おそいかかってきた！$"
JpBT_Text_WeirdTreeFled:
	.string "へんな きは どこかへ\n"
	.string "にげてしまった……$"

JpBT_Text_Welcome:
	.string "バトルタワーへ ようこそ！\p"
	.string "こちらで うけつけを すると\n"
	.string "バトルルームに はいれます$"
JpBT_Text_AskChallenge:
	.string "バトルルームに\n"
	.string "ちょうせん しますか？$"
JpBT_Text_LookingForward:
	.string "また の ちょうせんを\n"
	.string "おまちして おります$"
JpBT_Text_MustSave:
	.string "バトルルームに はいる まえに\n"
	.string "レポートを かきます\l"
	.string "よろしいですか？$"
JpBT_Text_WhichLevel:
	.string "バトルルームには\n"
	.string "レベル50と オープンレベルの\l"
	.string "2しゅるいが あります\p"
	.string "どちらに ちょうせん しますか？$"
JpBT_Text_SelectMons:
	.string "さんか させる ポケモンを\n"
	.string "えらんで ください$"
JpBT_Text_DirectYou:
	.string "それでは バトルルームへ\n"
	.string "ごあんない します$"
JpBT_Text_Info:
	.string "バトルタワーは ポケモン しょうぶの\n"
	.string "ために つくられた しせつです\p"
	.string "タワーの なかには\n"
	.string "バトルルームが たくさん あります\p"
	.string "バトルルームには レベル50と\n"
	.string "オープンレベルの 2しゅるいが\l"
	.string "あります\p"
	.string "レベル50の バトルルームには\n"
	.string "レベル50 いかの ポケモンが\l"
	.string "さんか できます\p"
	.string "あいての ポケモンも\n"
	.string "すべて レベル50です\p"
	.string "オープンレベルの バトルルームは\n"
	.string "どんな レベルの ポケモンでも\l"
	.string "さんか できます\p"
	.string "あいての ポケモンの レベルは\n"
	.string "あなたの ポケモンに あわせて\l"
	.string "かわります\p"
	.string "ただし あいての ポケモンが\n"
	.string "レベル60より ひくく なることは\l"
	.string "ありません\p"
	.string "それぞれの バトルルームでは\n"
	.string "7にんの トレーナーが\l"
	.string "まちかまえて います\p"
	.string "7にん すべてに かてば\n"
	.string "すてきな しょうひんを さしあげます\p"
	.string "とちゅうで レポートを かいて\n"
	.string "ひとやすみ する ことも できます\p"
	.string "ただし きちんと レポートを\n"
	.string "かかないと ちょうせんを\l"
	.string "つづけることが できません$"
JpBT_Text_NotEligible50:
	.string "もうしわけ ございません！\p"
	.string "さんか できる ポケモンが\n"
	.string "3びき そろって いません\p"
	.string "レベル50 いかの ちがう しゅるいの\n"
	.string "ポケモンが 3びき ひつようです\p"
	.string "もたせる どうぐも\n"
	.string "ちがう ものに して ください\p"
	.string "タマゴは さんか できません\p"
	.string "じゅんびが できたら\n"
	.string "また おこし ください$"
JpBT_Text_NotEligibleOpen:
	.string "もうしわけ ございません！\p"
	.string "さんか できる ポケモンが\n"
	.string "3びき そろって いません\p"
	.string "ちがう しゅるいの ポケモンが\n"
	.string "3びき ひつようです\p"
	.string "もたせる どうぐも\n"
	.string "ちがう ものに して ください\p"
	.string "タマゴは さんか できません\p"
	.string "じゅんびが できたら\n"
	.string "また おこし ください$"
JpBT_Text_DidntSave:
	.string "もうしわけ ございません！\p"
	.string "まえに ちょうせんを やめたとき\n"
	.string "レポートを かいて いませんでした\p"
	.string "そのため これまでの ちょうせんは\n"
	.string "むこうと なりました$"
JpBT_Text_Beat7:
	.string "おめでとう ございます！\n"
	.string "7にんの トレーナーに かちました！\p$"
JpBT_Text_Prize:
	.string "ちょうせんに せいこう したので\n"
	.string "すてきな しょうひんを どうぞ！\p$"
JpBT_Text_ReceivedPrize:
	.string "{PLAYER}は しょうひんの\n"
	.string "{STR_VAR_1}を うけとった！$"
JpBT_Text_BagFull:
	.string "あら バッグが いっぱいの\n"
	.string "ようですね\p"
	.string "バッグを せいりしてから\n"
	.string "また おこし ください$"
JpBT_Text_ThanksForPlaying:
	.string "ごくろうさまでした！\p$"
JpBT_Text_RecordSaved:
	.string "きろくを レポートに かきます\n"
	.string "しょうしょう おまち ください$"
JpBT_Text_BeenWaiting:
	.string "おまちして おりました！\p$"
JpBT_Text_WillSave:
	.string "バトルルームに はいる まえに\n"
	.string "レポートを かきます\l"
	.string "しょうしょう おまち ください$"
JpBT_Text_Next50th:
	.string "いよいよ 50にんめの\n"
	.string "トレーナーとの たいせんです\p"
	.string "これからは 7にん れんしょう\n"
	.string "するたびに ポケモンに\l"
	.string "きねんの リボンを さしあげます\p"
	.string "がんばって ください！$"
JpBT_Text_Ribbons:
	.string "7にんの つよい トレーナーに\n"
	.string "れんしょう した きねんの\l"
	.string "リボンです\p"
	.string "{PLAYER}は リボンを もらった！$"
JpBT_Text_RibbonsPut:
	.string "{PLAYER}は ちょうせんした\n"
	.string "ポケモンに リボンを つけた$"
JpBT_Text_LobbyWorker:
	.string "やあ やあ！\n"
	.string "きみは どこから きたんだい？\p"
	.string "……\p"
	.string "カントーの マサラタウン？\n"
	.string "それは ずいぶん とおくから！$"
JpBT_Text_LobbyCooltrainer:
	.string "なんかい れんしょう したかが\n"
	.string "きろく されるのよ\p"
	.string "きろくは うけつけの よこに\n"
	.string "はりだされて いるわ$"
JpBT_Text_LobbyBoy:
	.string "バトルタワーに はいったら\n"
	.string "まけるか 7にんに かつまで\l"
	.string "でられないんだ\p"
	.string "じしんが ついてから\n"
	.string "ちょうせん した ほうが いいよ$"
JpBT_Text_Scott28Wins:
	.string "スコット“きみの うわさは\n"
	.string "きいてるよ！\p"
	.string "バトルタワーで 28にん\n"
	.string "れんしょう したんだって？\p"
	.string "すごいじゃないか！\n"
	.string "これを うけとって くれ！$"
JpBT_Text_ScottExplainAurora:
	.string "その チケットを クチバこうの\n"
	.string "ふねのりに みせると いい\p"
	.string "ナナシマの 6のしまの みなみに\n"
	.string "ある ちいさな しまに\l"
	.string "つれていって くれるよ\p"
	.string "ふしぎな いしが ある だけの\n"
	.string "しまだけど\p"
	.string "ひとが いなくて しずかな\n"
	.string "いい ところさ！$"
JpBT_Text_ScottGaveAurora:
	.string "これからも きみの かつやくを\n"
	.string "きたいして いるよ！$"

JpBT_Text_WillRestore:
	.string "ポケモンを かいふく します$"
JpBT_Text_AskReady:
	.string "つぎは {STR_VAR_1}にんめの\n"
	.string "あいてです よろしいですか？$"
JpBT_Text_AskSaveQuit:
	.string "レポートを かいて\n"
	.string "ゲームを おわりますか？$"
JpBT_Text_AskCancel:
	.string "バトルルームの ちょうせんを\n"
	.string "やめますか？$"
JpBT_Text_Saving:
	.string "レポートを かいています\n"
	.string "でんげんを きらないで ください$"
JpBT_Text_Saved:
	.string "{PLAYER}は\n"
	.string "レポートに しっかり かきのこした！$"

@ ------------------------------------------------------------------ tilesets (FRLG+ gTileset_BattleFrontier / gTileset_BattleFrontierOutsideEast)
	.align 2
	.global gJpTileset_BattleFrontier
gJpTileset_BattleFrontier:
	.byte 1, 1, 0, 0
	.4byte gJpBFTiles, gJpBFPalettes, gJpBFMetatiles, 0, gJpBFAttrs
	.align 2
	.global gJpTileset_BattleFrontierOutsideEast
gJpTileset_BattleFrontierOutsideEast:
	.byte 1, 1, 0, 0
	.4byte gJpBFETiles, gJpBFEPalettes, gJpBFEMetatiles, InitTilesetAnim_JpBattleFrontierOutsideEast, gJpBFEAttrs
	.align 2
gJpBFTiles:
	.incbin "data/hooks/btts/bf_tiles.4bpp.lz"
	.align 2
gJpBFPalettes:
	.incbin "data/hooks/btts/bf_pals.bin"
	.align 2
gJpBFMetatiles:
	.incbin "data/hooks/btts/bf_metatiles.bin"
	.align 2
gJpBFAttrs:
	.incbin "data/hooks/btts/bf_attrs.bin"
	.align 2
gJpBFETiles:
	.incbin "data/hooks/btts/bfe_tiles.4bpp.lz"
	.align 2
gJpBFEPalettes:
	.incbin "data/hooks/btts/bfe_pals.bin"
	.align 2
gJpBFEMetatiles:
	.incbin "data/hooks/btts/bfe_metatiles.bin"
	.align 2
gJpBFEAttrs:
	.incbin "data/hooks/btts/bfe_attrs.bin"
	.align 2
	.global gJpBFEAnimFlag
gJpBFEAnimFlag:
	.incbin "data/hooks/btts/bfe_flag0.4bpp"
	.incbin "data/hooks/btts/bfe_flag1.4bpp"
	.incbin "data/hooks/btts/bfe_flag2.4bpp"
	.incbin "data/hooks/btts/bfe_flag3.4bpp"
	.align 2
	.global gJpBFEAnimFlower
gJpBFEAnimFlower:
	.incbin "data/hooks/btts/bfe_flower0.4bpp"
	.incbin "data/hooks/btts/bfe_flower1.4bpp"
	.incbin "data/hooks/btts/bfe_flower0.4bpp"
	.incbin "data/hooks/btts/bfe_flower2.4bpp"

@ new object sprites (gfx 170 Scott, 171 Sudowoodo); infos built by tools/bt_patch.py
	.global gJpBTOwScott
	.align 2
gJpBTOwScott:
	.incbin "data/hooks/btts/ow_scott.4bpp"
	.global gJpBTOwSudowoodo
gJpBTOwSudowoodo:
	.incbin "data/hooks/btts/ow_sudowoodo.4bpp"
