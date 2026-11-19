#include "global.h"
#include "event_data.h"
#include "script.h"
#include "fieldmap.h"
#include "field_player_avatar.h"
#include "field_fadetransition.h"
#include "field_weather.h"
#include "constants/flags.h"
// メニューに「パソコン」(赤フルカラーの「メニューからパソコン」)
// JP SetUpStartMenu_NormalField (0x0806E51C) is replaced; item 9 = パソコン (tables relocated in patch_port.py)

#define JpAppendToStartMenuItems ((void (*)(u8))0x0806E501)
#define JpStartMenuExitCallback  ((bool8 (*)(void))0x0806ECA9)
#define STARTMENU_JP_PC 9

extern const u8 EventScript_JpMenuPC[];

void JpSetUpStartMenu_NormalField(void)
{
    if (FlagGet(FLAG_SYS_POKEDEX_GET) == TRUE)
        JpAppendToStartMenuItems(0);
    if (FlagGet(FLAG_SYS_POKEMON_GET) == TRUE)
        JpAppendToStartMenuItems(1);
    JpAppendToStartMenuItems(2);
    if (FlagGet(FLAG_SYS_POKEMON_GET) == TRUE)
        JpAppendToStartMenuItems(STARTMENU_JP_PC);
    JpAppendToStartMenuItems(3);
    JpAppendToStartMenuItems(4);
    JpAppendToStartMenuItems(5);
    /* 「とじる」(6) は出さない：パソコンを足して 9こに なると 説明の まどの下に はみ出すため。Bボタンで とじられる */
}

bool8 JpStartMenuPcCallback(void)
{
    JpStartMenuExitCallback();
    ScriptContext_SetupScript(EventScript_JpMenuPC);
    return TRUE;
}

// EventScript_TurnOffPC: only redraw the "PC off" tile when the player really stands at a PC that was turned on
void JpMenuPc_IsFacingPcOn(void)
{
    s16 x = gSaveBlock1Ptr->pos.x + MAP_OFFSET, y = gSaveBlock1Ptr->pos.y + MAP_OFFSET;
    u16 id;
    switch (GetPlayerFacingDirection())
    {
    case DIR_NORTH: y--; break;
    case DIR_WEST: x--; y--; break;
    case DIR_EAST: x++; y--; break;
    }
    id = MapGridGetMetatileIdAt(x, y);
    gSpecialVar_Result = (id == 0x063 || id == 0x28A);
}

// JP StartMenu_FadeScreenIfLeavingOverworld (0x0806EB00): パソコン stays on the field like セーブ / とじる
#define JpStartMenuCallbackPtr (*(void **)0x02037024)
void JpStartMenu_FadeScreenIfLeavingOverworld(void)
{
    void *cb = JpStartMenuCallbackPtr;
    if (cb != (void *)0x0806EC51 && cb != (void *)0x0806ECA9 && cb != (void *)0x0806ECBD
     && cb != (void *)JpStartMenuPcCallback)
        FadeScreen(FADE_TO_BLACK, 0);
}
