#include "global.h"
#include "gflib.h"
#include "bg_regs.h"
#include "cable_club.h"
#include "credits.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "event_scripts.h"
#include "field_camera.h"
#include "field_control_avatar.h"
#include "field_effect.h"
#include "field_fadetransition.h"
#include "field_message_box.h"
#include "field_player_avatar.h"
#include "field_screen_effect.h"
#include "field_specials.h"
#include "field_tasks.h"
#include "field_weather.h"
#include "fieldmap.h"
#include "fldeff.h"
#include "heal_location.h"
#include "help_system.h"
#include "link.h"
#include "link_rfu.h"
#include "load_save.h"
#include "m4a.h"
#include "map_name_popup.h"
#include "map_preview_screen.h"
#include "metatile_behavior.h"
#include "money.h"
#include "new_game.h"
#include "new_menu_helpers.h"
#include "overworld.h"
#include "play_time.h"
#include "quest_log.h"
#include "quest_log_objects.h"
#include "random.h"
#include "renewable_hidden_items.h"
#include "roamer.h"
#include "safari_zone.h"
#include "save_location.h"
#include "scanline_effect.h"
#include "script.h"
#include "script_pokemon_util.h"
#include "start_menu.h"
#include "tileset_anims.h"
#include "trainer_pokemon_sprites.h"
#include "vs_seeker.h"
#include "wild_encounter.h"
#include "constants/cable_club.h"
#include "constants/event_objects.h"
#include "constants/maps.h"
#include "constants/region_map_sections.h"
#include "constants/songs.h"
#include "constants/sound.h"
#include "gunk_follower.h"

void LoadCurrentMapData(void);
void LoadObjEventTemplatesFromHeader(void);
void TrySetMapSaveWarpStatus(void);
void ClearTempFieldEventData(void);
void ResetCyclingRoadChallengeData(void);
void ChooseAmbientCrySpecies(void);
void SetDefaultFlashLevel(void);
void InitMap(void);
void DoCB1_Overworld_QuestLogPlayback(void);
void DoCB1_Overworld(u16 newKeys, u16 heldKeys);
void RoamerMoveToOtherLocationSet(void);
void UpdateLocationHistoryForRoamer(void);
void CB2_Overworld(void);
struct InitialPlayerAvatarState { u8 transitionFlags; u8 direction; bool8 hasDirectionSet; };
struct InitialPlayerAvatarState *GetInitialPlayerAvatarState(void);

void JpMaster_SyncHideFlag(void);
void LoadMapFromWarp(bool32 unused)
{
    bool8 isOutdoors;

    JpMaster_SyncHideFlag();
    DespawnFollowerSprite();
    LoadCurrentMapData();
    LoadObjEventTemplatesFromHeader();
    isOutdoors = IsMapTypeOutdoors(gMapHeader.mapType);

    TrySetMapSaveWarpStatus();
    ClearTempFieldEventData();
    ResetCyclingRoadChallengeData();
    RestartWildEncounterImmunitySteps();
    MapResetTrainerRematches(gSaveBlock1Ptr->location.mapGroup, gSaveBlock1Ptr->location.mapNum);
    SetSavedWeatherFromCurrMapHeader();
    ChooseAmbientCrySpecies();
    if (isOutdoors)
        FlagClear(FLAG_SYS_FLASH_ACTIVE);
    SetDefaultFlashLevel();
    Overworld_ClearSavedMusic();
    RunOnTransitionMapScript();
    TryRegenerateRenewableHiddenItems();
    UpdateLocationHistoryForRoamer();
    RoamerMoveToOtherLocationSet();
    QL_ResetDefeatedWildMonRecord();
    InitMap();
}

void CB1_Overworld(void)
{
    if (gMain.callback2 == CB2_Overworld)
    {
        if (QL_GetPlaybackState() == QL_PLAYBACK_STATE_RUNNING || gQuestLogState == QL_STATE_PLAYBACK)
            DoCB1_Overworld_QuestLogPlayback();
        else
        {
            DoCB1_Overworld(gMain.newKeys, gMain.heldKeys);
            UpdateFollowerPokemon();
        }
    }
}

void InitObjectEventsLocal(void)
{
    s16 x, y;
    struct InitialPlayerAvatarState *player;

    gTotalCameraPixelOffsetX = 0;
    gTotalCameraPixelOffsetY = 0;
    ResetObjectEvents();
    GetCameraFocusCoords(&x, &y);
    player = GetInitialPlayerAvatarState();
    InitPlayerAvatar(x, y, player->direction, gSaveBlock2Ptr->playerGender);
    SetPlayerAvatarTransitionFlags(player->transitionFlags);
    ResetInitialPlayerAvatarState();
    TrySpawnObjectEvents(0, 0);
    SpawnFollowerSprite();
    TryRunOnWarpIntoMapScript();
}

void ReloadObjectsAndRunReturnToFieldMapScript(void)
{
    SpawnObjectEventsOnReturnToField(0, 0);
    SpawnFollowerSprite();
    RunOnReturnToFieldMapScript();
}
