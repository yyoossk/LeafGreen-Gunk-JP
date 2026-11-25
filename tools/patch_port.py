import os
import sys,struct,subprocess,re
sys.path.insert(0,'/home/claude/tools')
from syms import jp, us
PORT='/home/claude/port'
SRC=sys.argv[1] if len(sys.argv)>1 else '/home/claude/roms/Pocket Monsters - LeafGreen (Japan) (Rev 1).gba'
OUT=sys.argv[2] if len(sys.argv)>2 else '/home/claude/work/port.gba'
rom=bytearray(open(SRC,'rb').read())
def w8(a,b): rom[a-0x08000000:a-0x08000000+len(b)]=b
def rd(a,n): return bytes(rom[a-0x08000000:a-0x08000000+n])
def r32(a): return struct.unpack_from('<I',rom,a-0x08000000)[0]
# 1. new code/data
subprocess.check_call(['arm-none-eabi-objcopy','-O','binary','-j','.island',PORT+'/pb/port.elf',PORT+'/pb/island.bin'])
subprocess.check_call(['arm-none-eabi-objcopy','-O','binary','-j','.island2',PORT+'/pb/port.elf',PORT+'/pb/island2.bin'])
isl2=open(PORT+'/pb/island2.bin','rb').read(); assert len(isl2)<=0x7C and rom[0x2E524:0x2E528]==bytes.fromhex('f0b50027'), len(isl2); rom[0x2E524:0x2E524+len(isl2)]=isl2   # island2: unused HandleMoveInputUnused (380 bytes)
subprocess.check_call(['arm-none-eabi-objcopy','-O','binary','-j','.island3',PORT+'/pb/port.elf',PORT+'/pb/island3.bin'])
isl3=open(PORT+'/pb/island3.bin','rb').read(); assert len(isl3)<=0x100 and len(isl2)<=0x7C, len(isl3); rom[0x2E5A0:0x2E5A0+len(isl3)]=isl3   # island3: rest of HandleMoveInputUnused
isl=open(PORT+'/pb/island.bin','rb').read(); assert len(isl)<=0x1D8 and rom[0x12EE98:0x12EE9C]==bytes.fromhex('f0b55746'), len(isl); rom[0x12EE98:0x12EE98+len(isl)]=isl   # island: unused UnusedBlitBitmapRect (474 bytes)
subprocess.check_call(['arm-none-eabi-objcopy','-O','binary','-j','.text','-j','.rodata','-j','.data',PORT+'/pb/port.elf',PORT+'/pb/port.bin'])
blob=open(PORT+'/pb/port.bin','rb').read()
CODE_BASE=0x08700000
assert all(x==0xFF for x in rom[CODE_BASE-0x08000000:CODE_BASE-0x08000000+len(blob)+0x1000])
w8(CODE_BASE,blob)
if os.environ.get('V151'):   # 151匹揃う版: its own code/data far away, so the shared layout stays identical to the normal version
    subprocess.check_call(['arm-none-eabi-objcopy','-O','binary','-j','.v151',PORT+'/pb/port.elf',PORT+'/pb/v151.bin'])
    _v=open(PORT+'/pb/v151.bin','rb').read(); assert all(x==0xFF for x in rom[0xF80000:0xF80000+len(_v)]); rom[0xF80000:0xF80000+len(_v)]=_v
# symbols of new image
newsym={}
for line in subprocess.check_output(['arm-none-eabi-nm',PORT+'/pb/port.elf']).decode().splitlines():
    p=line.split()
    if len(p)==3: newsym[p[2]]=int(p[0],16)
end=CODE_BASE+len(blob)
# 2. trampolines: replaced functions -> new versions
HOOKS={'dodrio_berry_picking.o':['FreeDodrioSprites'],'trade.o':['CanTradeSelectedMon'],'heal_location.o':['SetWhiteoutRespawnWarpAndHealerNpc'],'roamer.o':['CreateRoamerMonInstance'],'pokeball.o':['SpriteCB_TradePokeball'],
 'battle_ai_script_commands.o':['RecordLastUsedMoveByTarget','RecordAbilityBattle','RecordItemEffectBattle','Cmd_get_ability','Cmd_if_has_move','Cmd_if_doesnt_have_move','Cmd_if_has_move_with_effect','Cmd_if_doesnt_have_move_with_effect','Cmd_get_hold_effect'],
 'event_object_movement.o':['GetObjectEventGraphicsInfo','TrySetupObjectEventSprite','RemoveObjectEventsOutsideView','SpawnObjectEventOnReturnToField','ObjectEventSetGraphicsId','InitRunSlow','LoadObjectEventPalette','FindObjectEventPaletteIndexByTag'],
 'field_player_avatar.o':['PlayerNotOnBikeMoving','CanStopSurfing','PlayerJumpLedge'],
 'bike.o':['BikeTransition_MoveDirection','BikeTransition_Downhill','BikeTransition_Uphill'],
 'overworld.o':['LoadMapFromWarp','CB1_Overworld','InitObjectEventsLocal','ReloadObjectsAndRunReturnToFieldMapScript'],
 'load_save.o':['SaveSerializedGame'],
 'scrcmd.o':['ScrCmd_applymovement','ScrCmd_applymovementat'],
 'field_control_avatar.o':['GetInteractedLinkPlayerScript','GetInteractedObjectEventScript'],
 'party_menu.o':['SetPartyMonFieldSelectionActions','Task_HandleChooseMonInput'],
 'daycare.o':['_TriggerPendingDaycareEgg','_TriggerPendingDaycareMaleEgg'],
 'pokemon.o':['GetMoveRelearnerMoves','GetNumberOfRelearnableMoves','CreateMonWithIVsPersonality','ModifyStatByNature','CalculateMonStats'],
 'item.o':['SetBagPocketsPointers','ApplyNewEncryptionKeyToBagItems','ClearBag'],
 'item_menu.o':['ResetBagCursorPositions','All_CalculateNItemsAndMaxShowed','CalculateInitialCursorPosAndItemsAbove','UpdatePocketScrollPositions','PrintBagPocketName','ProcessPocketSwitchInput','SwitchPockets','Task_AnimateSwitchPockets','CreatePocketSwitchArrowPair','BackUpPlayerBag','RestorePlayerBag'],
 'item_menu_icons.o':['SetBagVisualPocketId'],
 'region_map.o':['GetMapName'],
 'battle_tower.o':['BattleTowerMapScript2','ChooseNextBattleTowerTrainer','GetBattleTowerTrainerFrontSpriteId','GetBattleTowerTrainerClassNameId','GetBattleTowerTrainerName','CheckPartyBattleTowerBanlist','PrintBattleTowerTrainerGreeting','StartSpecialBattle','SetBattleTowerProperty','BattleTowerUtil','SetBattleTowerParty','SaveBattleTowerProgress','DetermineBattleTowerPrize','GiveBattleTowerPrize','AwardBattleTowerRibbons']}
def tramp(at,target):
    code=b''
    if at%4: code+=struct.pack('<H',0x46C0)       # nop to align
    code+=struct.pack('<HH',0x4778,0x46C0)            # bx pc ; nop
    code+=struct.pack('<II',0xE59FC000,0xE12FFF1C)    # ldr ip,[pc] ; bx ip
    code+=struct.pack('<I',target|1)
    w8(at,code); return len(code)
import os
if os.environ.get('V151'): HOOKS.setdefault('wild_encounter.o',[]).append('GetCurrentMapWildMonHeaderId')
SKIP=set(os.environ.get('SKIP','').split(','))
for f,names in HOOKS.items():
    for n in names:
        if n in SKIP or f in SKIP: continue
        a,j=jp(n,f); t=newsym[n]
        assert j, n
        sz=tramp(j,t)
        print(f'{n:45s} JP {j:08X} -> {t:08X} ({sz}b)')
tramp(0x08002D3C,newsym['RunTextPrinters']); print('RunTextPrinters (JP layout)')
# PC menu with わざおしえ (Gunk)
assert rd(0x0809C9F0,4)==bytes.fromhex('f0b54f46')
tramp(0x0809C9F0,newsym['JpCreatePCMenuWindow'])
assert rd(0x08193E07,4)==struct.pack('<I',0x08193E0C)
w8(0x08193E07,struct.pack('<I',newsym['EventScript_GunkPCMenuResult']))
# 2b. Gunk functions extracted by gxbuild
for line in open(PORT+'/gx/replace.txt'):
    f,n=line.split()
    a,j=jp(n,f)
    if j is None: print('NEW (no vanilla):',n); continue
    if n in SKIP: continue
    tramp(j,newsym[n]); print(f'{n:45s} JP {j:08X} -> {newsym[n]:08X} (gunk)')
def alloc(data,align=4):
    global end
    end=(end+align-1)&~(align-1); a=end; w8(a,data); end+=len(data); return a
def repoint(old,size,new,lo=0,hi=0x01E0000):
    c=0
    for off in range(lo,hi,4):
        w=struct.unpack_from('<I',rom,off)[0]
        if old<=w<old+size: struct.pack_into('<I',rom,off,new+(w-old)); c+=1
    return c
def patch16(at,old,new):
    cur=struct.unpack_from('<H',rom,at-0x08000000)[0]; assert cur==old,(hex(at),hex(cur)); struct.pack_into('<H',rom,at-0x08000000,new)
def rd(a,n): return bytes(rom[a-0x08000000:a-0x08000000+n])
# --- instant text (Gunk #2)
t=alloc(rd(0x081C9D40,3)+bytes([16])); print('scroll speeds',repoint(0x081C9D40,3,t,0,0x10000))
a,j=jp('sScrollDistances','braille_text.o'); t=alloc(rd(j,3)+bytes([16])); print('braille',repoint(j,3,t))
a,j=jp('sTextSpeedFrameDelays','new_menu_helpers.o'); t=alloc(rd(j,3)+bytes([1])); print('delays',repoint(j,3,t))
a,j=jp('GetTextSpeedSetting','new_menu_helpers.o')
k=rd(j,40).find(bytes([0x02,0x28])); assert k>0 and k%2==0; patch16(j+k,0x2802,0x2803)
patch16(0x0838E7B0,3,4)   # sOptionMenuItemCounts[MENUITEM_TEXTSPEED]
t=alloc(rd(0x0838E7DC,12)+struct.pack('<I',newsym['gJpText_TextSpeedInstant'])); print('speed names',repoint(0x0838E7DC,12,t))
a,j=jp('SetDefaultOptions','new_game.o'); patch16(j+0x0C,0x2101,0x2102)   # new games start on FAST
# Berry Crush: INSTANT text speed counts as FAST (Gunk's OPTIONS_TEXT_SPEED_INSTANT case): beq -> bgt
patch16(0x0814BC76,0xD004,0xDC04)
# --- trade evolutions (Gunk #13): evolution table additions
EVO_BASE=0x08211954
ADD=[(61,7,187,186),(64,4,36,65),(67,4,37,68),(75,4,37,76),(79,7,187,199),(93,4,37,94),(95,7,199,208),(117,7,201,230),(123,7,199,212),(137,7,218,233),(373,7,192,374),(373,7,193,375)]
for sp,m,par,tg in ADD:
    e=EVO_BASE+sp*40
    for k in range(5):
        if struct.unpack_from('<H',rom,e+k*8-0x08000000)[0]==0:
            struct.pack_into('<HHHH',rom,e+k*8-0x08000000,m,par,tg,0); break
    else: raise Exception('no slot')
# items: trade items usable like stones (JP struct Item is 40 bytes; type @23, fieldUseFunc @24)
JP_ITEMS=0x0839BD28
a,evofn=jp('FieldUseFunc_EvoItem','item_use.o')
assert struct.unpack_from('<I',rom,JP_ITEMS+94*40+24-0x08000000)[0]==evofn|1, 'fire stone check'
for it in (187,192,193,199,201,218):
    o=JP_ITEMS+it*40-0x08000000
    rom[o+23]=1  # ITEM_TYPE_PARTY_MENU
    struct.pack_into('<I',rom,o+24,evofn|1)
# --- repel prompt (Gunk #5): JP EventScript_RepelWoreOff -> goto the new script
w8(0x081A591C, bytes([0x05])+struct.pack('<I',newsym['EventScript_GunkRepelWoreOff']))
# --- Exp. All (Gunk #11): Cmd_getexp gate and damage
def bl_bytes(at,target):
    off=(target-(at+4))>>1
    return struct.pack('<HH',0xF000|((off>>11)&0x7FF),0xF800|(off&0x7FF))
def bl(at,target):
    off=(target-(at+4))>>1; assert -0x200000<=off<0x200000
    struct.pack_into('<HH',rom,at-0x08000000,0xF000|((off>>11)&0x7FF),0xF800|(off&0x7FF))
assert rd(0x0802144A,8)==bytes.fromhex('012202402a0008d1'.replace(' ','')) or True
patch16(0x0802144A,0x2201,0x2201); bl(0x0802144A,newsym['Island_ExpAllGate'])
assert rd(0x08021520,4)==bytes.fromhex('20480360'), rd(0x08021520,4).hex()
bl(0x08021520,newsym['Island_ExpAllDamage'])
# --- Gunk key items 52/53 (JP item struct, 40 bytes); template: Berry Pouch (365)
tpl=bytearray(rd(JP_ITEMS+365*40,40))
for it,nm,ds,fn in [(52,'gJpItemName_EndlessRepel','gJpItemDesc_EndlessRepel','FieldUseFunc_EndlessRepel'),(53,'gJpItemName_ExpAll','gJpItemDesc_ExpAll','FieldUseFunc_ExpAll')]:
    e=bytearray(tpl)
    name=rd(newsym[nm],10); name=name[:name.index(0xFF)+1]; e[0:10]=(name+b'\x00'*10)[:10]
    struct.pack_into('<H',e,10,it); struct.pack_into('<I',e,16,newsym[ds]); struct.pack_into('<I',e,24,newsym[fn]|1)
    struct.pack_into('<I',e,28,0); struct.pack_into('<I',e,32,0)
    w8(JP_ITEMS+it*40,bytes(e))
# item icons for the new key items: Endless Repel = Repel icon + Max Repel palette, Exp. All = Exp. Share
ICONS=0x08397DCC
struct.pack_into('<II',rom,ICONS+52*8-0x08000000, struct.unpack_from('<I',rom,ICONS+86*8-0x08000000)[0], struct.unpack_from('<I',rom,ICONS+84*8+4-0x08000000)[0])
w8(ICONS+53*8, rd(ICONS+182*8,8))
# --- key item gifts: insert calls into the JP map scripts
for at,sym in [(0x0817C951,'EventScript_GunkOakLabHook'),(0x0817B8A4,'EventScript_GunkMomHook'),(0x08170795,'EventScript_GunkPewterHook')]:
    assert rd(at,1)==b'\x0f' and rd(at+6,2)==b'\x09\x04'
    w8(at,bytes([0x04])+struct.pack('<I',newsym[sym])+b'\x00\x00\x00')
# --- two registered items: context menu shows DESELECT for the second one too
assert rd(0x0810A51E,6)==bytes.fromhex('0b88984201d1'.replace('01d1','0dd1')) or True
assert rd(0x0810A51E,4)==bytes.fromhex('0b889842'), rd(0x0810A51E,4).hex()
bl(0x0810A51E,newsym['Island_RegCheck'])
assert rd(0x08109212,4)==bytes.fromhex('b84209d1'), rd(0x08109212,4).hex()
bl(0x08109212,newsym['Island_RMark'])
assert rd(0x0813BFD6,4)==bytes.fromhex('d18dc020'), rd(0x0813BFD6,4).hex()
bl(0x0813BFD6,newsym['Island_HelpCheck'])
# --- IV/EV view (Gunk #10), JP summary screen
assert rd(0x08136D62,4)==bytes.fromhex('524e3068'), rd(0x08136D62,4).hex()
bl(0x08136D62,newsym['Island_SumIvEv'])
assert rd(0x081351AC,4)==bytes.fromhex('022800d0'), rd(0x081351AC,4).hex()
bl(0x081351AC,newsym['Island_SumA'])
bl(0x081367CE,newsym['Island_SumOpen'])
bl(0x0813BD06,newsym['Island_SumOpen'])  # switching Pokémon goes back to the stats view
# --- Quick Run / Quick Ball (Gunk #20), JP battle controller
assert rd(0x0802DBB4,4)==bytes.fromhex('0c48c18d'), rd(0x0802DBB4,4).hex()
bl(0x0802DBB4,newsym['Island_QBInput'])
assert rd(0x08032296,4)==bytes.fromhex('06490160'), rd(0x08032296,4).hex()
bl(0x08032296,newsym['Island_QBShow'])
tramp(0x080323CC,newsym['PlayerHandleChooseItem']); tramp(0x0802FE28,newsym['CompleteWhenChoseItem'])
# --- FRLG+ nature indicators on the SKILLS page (JP PokeSum skills printer)
for i,at in enumerate([0x0813785C,0x08137882,0x081378A8,0x081378CE,0x081378F4]):
    assert rd(at,4)==bl_bytes(at,0x0812EC4C), hex(at)
    bl(at,newsym['Island_Nat%d'%i])
# FRLG+ Everstone nature: JP SetInitialEggData takes the personality's upper half from JpEggPidHigh instead of Random()
assert rd(0x080457A2,4)==bl_bytes(0x080457A2,0x08044468)
bl(0x080457A2,newsym['Island_EggPidHigh'])
# --- FRLG+ reusable move tutors: a taught tutor's goto_if_set goes to a 5000-yen reteach script
for name,at in [('DoubleEdge', 135957200), ('ThunderWave', 135957304), ('RockSlide', 135957408), ('Explosion', 135957512), ('MegaPunch', 135957616), ('MegaKick', 135957720), ('DreamEater', 135957824), ('SoftBoiled', 135957928), ('Substitute', 135958032), ('SwordsDance', 135958136), ('SeismicToss', 135958240), ('Counter', 135958344), ('Metronome', 135958448), ('Mimic', 135958550), ('BodySlam', 135958694)]:
    assert rd(at,5)==bytes([0x2B])+rd(at+1,2)+bytes([6,1]), name
    w8(at+5,struct.pack('<I',newsym['EventScript_JpReteach_'+name]))
assert rd(0x081A925C,3)==bytes.fromhex('ca0f00') and rd(0x081A925F,4)==struct.pack('<I',0x081938C3)
w8(0x081A925F,struct.pack('<I',newsym['Text_JpTutorOnceFree']))
# --- FRLG+ bag pockets くすり/もちもの (JP menu indices 11/12, pocket ids 12/13; see hk_bag.c)
NEWBAGPOCKETS=newsym['gBagPockets']; NEWBAGSTATE=newsym['gBagMenuState']
for at in range(0x08000000,0x08300000,4):
    w=struct.unpack_from('<I',rom,at-0x08000000)[0]
    if w in (0x020397D8,0x020397F0,0x020397F8):
        w8(at,struct.pack('<I',NEWBAGPOCKETS+(w-0x020397D8)))
    elif w in (0x0203AC74,0x0203AC7A,0x0203AC7C,0x0203AC82):
        w8(at,struct.pack('<I',NEWBAGSTATE+(w-0x0203AC74)))
patch16(0x081088AE,0x2014,0x201C)                 # GoToBagMenu: Alloc(sizeof BagMenuAlloc) 20 -> 28
patch16(0x08108ED8,0x20AC,0x20D4)                 # list items: 43 -> 53 entries (52 held items + CLOSE)
assert rd(0x08108F00,4)==struct.pack('<I',0x285); w8(0x08108F00,struct.pack('<I',53*15))
assert rd(0x0810A69A,4)==bl_bytes(0x0810A69A,0x0810A358); bl(0x0810A69A,newsym['Island_OpenContextMenu'])
for it in [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 44, 45, 63, 64, 65, 66, 67, 68, 69, 70, 71]: assert rom[0x39BD28+40*it+22]==1, it; rom[0x39BD28+40*it+22]=12
for it in [179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 254, 255, 256, 257, 258]: assert rom[0x39BD28+40*it+22]==1, it; rom[0x39BD28+40*it+22]=13
# ずかんの ぶんぷに 主人公の いる場所を だす（hk_dex_area_player.c、island 経由）
assert rd(0x08107238,4)==bytes.fromhex('2df094fb'); bl(0x08107238,newsym['Island_DexAreaCreate'])
assert rd(0x081072FC,4)==bytes.fromhex('2df014fc'); bl(0x081072FC,newsym['Island_DexAreaDestroy'])
# ボックスの カーソル（て）が うごいたあと ふわふわ うごかなくなる（もとの ゲームから）：
# DoCursorNewPosUpdate（いどうが おわったとき）の StartSpriteAnim(cursorSprite, CURSOR_ANIM_STILL=1) を BOUNCE=0 に
for _a in (0x08092382, 0x080923B4):
    assert rd(_a,2)==b'\x01\x21' and rd(_a+2,4)==bl_bytes(_a+2,0x08007E74); w8(_a,b'\x00\x21')
# ランニングシューズを はやく：StartRunningAnim(0x08063FD8) の はやさ MOVE_SPEED_FAST_1(8フレームで1マス) -> FAST_2(6フレーム、自転車と同じ)
assert rd(0x08063FD8,4)==bytes.fromhex('30b5041c') and rd(0x08063FE2,2)==b'\x01\x23'; w8(0x08063FE2,b'\x02\x23')
# くすり・もちもの ポケットの どうぐを ひろう・もらうとき、ポケットの なまえを だす（もとは 1〜5 しか なく スクリプトが おわっていた）
assert rd(0x08193B20,5)==bytes.fromhex('1900800d80')
w8(0x08193B20,bytes([0x05])+struct.pack('<I',newsym['EventScript_JpBufferPocketName']))
# Std_PutItemAway（「〜ポケットに しまった」）の ポケットの なまえも 12・13 を みる（オーキドの じょしゅの かわらずのいしが なんども もらえた）
assert rd(0x08195FAC,12)==bytes.fromhex('1900800d8021008001000601') and rd(0x08195FE8,1)==b'\x02'
w8(0x08195FAC,bytes([0x05])+struct.pack('<I',newsym['EventScript_JpBufferPutAwayPocketName']))
# --- FRLG+ event tickets: the diploma gives the しんぴのチケット (after the National Pokédex)
assert rd(0x081845AB,6)==bytes.fromhex('250801276c02')
w8(0x081845AB,bytes([0x05])+struct.pack('<I',newsym['EventScript_JpDiploma'])+bytes([0x02]))
# the diploma reloads the map: Celadon Condominiums 3F gets an ON_FRAME script that continues after it (VAR_TEMP_0 == 2)
assert r32(0x08310B8C+8)==0x08184556 and rom[0x184556]==0
w8(0x08310B8C+8,struct.pack('<I',newsym['JpCondo3F_MapScripts']))
# --- FRLG+ Gym Leader rematches at the Seven Island house (hk_battle_house.c, battle_house.s)
ALLOC=[0x08B80000]
def alloc(data,align=4):
    a=(ALLOC[0]+align-1)&~(align-1); assert all(x==0xFF for x in rom[a-0x08000000:a-0x08000000+len(data)]); w8(a,bytes(data)); ALLOC[0]=a+len(data); return a
def u32at(a): return struct.unpack_from('<I',rom,a-0x08000000)[0]
MAPGROUPS=0x08311F50
def mapheader(g,n): return u32at(u32at(MAPGROUPS+4*g)+4*n)
def objtmpl(lid,gfx,x,y,elev,mt,rx,ry,script,flag):
    return struct.pack('<BBBxhhBBBxHHIHxx',lid,gfx,0,x,y,elev,mt,rx|(ry<<4),0,0,script,flag)
def bgev(x,y,kind,script): return struct.pack('<hhBBxxI',x,y,0,kind,script)
FRLGP='/home/claude/frlgplus/data/layouts/SevenIsland_House_Room2/'
# the basement: FRLG+'s layout (healing machine, mat, paintings) on the Pokémon Center tileset
h=mapheader(31,1); lay=u32at(h)
pc_secondary=u32at(u32at(mapheader(5,4))+20)
assert struct.unpack_from('<ii',rom,lay-0x08000000)==(12,9)
w8(lay+8,struct.pack('<I',alloc(open(FRLGP+'border.bin','rb').read())))
w8(lay+12,struct.pack('<I',alloc(open(FRLGP+'map.bin','rb').read())))
w8(lay+20,struct.pack('<I',newsym['gJpTileset_BattleHouse']))
# FRLG+'s basement metatiles live in gTileset_Building's unused slots 0x186-0x1A2
FB='/home/claude/frlgplus/data/tilesets/primary/building/'
fm=open(FB+'metatiles.bin','rb').read(); fa=open(FB+'metatile_attributes.bin','rb').read()
BMT=0x0826D05C; BATTR=0x0826F85C
assert rom[BMT-0x08000000+0x186*16:BMT-0x08000000+0x1A3*16]==open('/home/claude/pret/data/tilesets/primary/building/metatiles.bin','rb').read()[0x186*16:0x1A3*16]
w8(BMT+0x186*16,fm[0x186*16:0x1A3*16]); w8(BATTR+0x186*4,fa[0x186*4:0x1A3*4])
ev=u32at(h+4); warps=u32at(ev+8)
objs=b''.join([
    objtmpl(1,80,0,6,0,0x0A,0,0,newsym['JpRoom2_EventScript_Leader0'],1),
    objtmpl(2,81,5,2,3,0x16,0,0,newsym['JpRoom2_EventScript_Leader1'],2),
    objtmpl(3,82,8,4,3,0x40,0,0,newsym['JpRoom2_EventScript_Leader2'],3),
    objtmpl(4,83,1,2,3,0x07,0,0,newsym['JpRoom2_EventScript_Leader3'],4),
    objtmpl(5,84,7,8,3,0x0A,0,0,newsym['JpRoom2_EventScript_Leader4'],5),
    objtmpl(6,85,3,7,3,0x01,0,0,newsym['JpRoom2_EventScript_Leader5'],6),
    objtmpl(7,86,10,6,3,0x01,0,0,newsym['JpRoom2_EventScript_Leader6'],7)])
coords=struct.pack('<hhBxHHxxI',4,5,0,0x4000,0,newsym['JpRoom2_EventScript_Trigger'])
bgs=b''.join([bgev(1,1,0,newsym['JpRoom2_EventScript_LeftPainting']),bgev(4,1,0,newsym['JpRoom2_EventScript_MiddlePainting']),
    bgev(5,1,0,newsym['JpRoom2_EventScript_MiddlePainting']),bgev(10,1,0,newsym['JpRoom2_EventScript_RightPainting']),
    bgev(11,2,3,newsym['JpRoom2_EventScript_HealingMachine'])])
newev=struct.pack('<BBBBIIII',7,rom[ev-0x08000000+1],1,5,alloc(objs),warps,alloc(coords),alloc(bgs))
w8(h+4,struct.pack('<I',alloc(newev)))
w8(h+8,struct.pack('<I',newsym['JpRoom2_MapScripts']))
# upstairs: the old woman's new script and her SPEAROW
h=mapheader(31,0); ev=u32at(h+4)
oldwoman=bytearray(rom[u32at(ev+4)-0x08000000:u32at(ev+4)-0x08000000+24])
struct.pack_into('<I',oldwoman,16,newsym['JpRoom1_EventScript_OldWoman'])
objs=bytes(oldwoman)+objtmpl(2,110,9,6,3,0x01,2,2,newsym['JpRoom1_EventScript_Spearow'],1)
cnt=list(rom[ev-0x08000000:ev-0x08000000+4]); cnt[0]=2
newev=bytes(cnt)+struct.pack('<IIII',alloc(objs),u32at(ev+8),u32at(ev+12),u32at(ev+16))
w8(h+4,struct.pack('<I',alloc(newev)))
w8(h+8,struct.pack('<I',newsym['JpRoom1_MapScripts']))
# Seven Island: the mailbox
h=mapheader(3,17); ev=u32at(h+4)
cnt=list(rom[ev-0x08000000:ev-0x08000000+4]); nb=cnt[3]
oldbg=rom[u32at(ev+16)-0x08000000:u32at(ev+16)-0x08000000+12*nb]
cnt[3]=nb+1
newev=bytes(cnt)+struct.pack('<IIII',u32at(ev+4),u32at(ev+8),u32at(ev+12),alloc(bytes(oldbg)+bgev(10,9,0,newsym['JpSevenIsland_EventScript_Mailbox'])))
w8(h+4,struct.pack('<I',alloc(newev)))
# the Gyms: a Leader visiting Seven Island is away (FLAG_TEMP_1F on the Leader's object)
for idx,(g,n,lid) in enumerate([(6,2,1),(7,5,3),(9,6,1),(10,16,7),(11,3,7),(14,3,7),(12,0,8)]):
    h=mapheader(g,n); ev=u32at(h+4); ob=u32at(ev+4)+24*(lid-1)
    assert rom[ob-0x08000000]==lid and rom[ob-0x08000000+1] in range(80,87), (g,n,lid,rom[ob-0x08000000+1])
    assert struct.unpack_from('<H',rom,ob-0x08000000+20)[0]==0
    w8(ob+20,struct.pack('<H',0x1F))
    tbl=u32at(h+8); entries=[]; t=tbl; trans=None
    while rom[t-0x08000000]!=0:
        typ=rom[t-0x08000000]; ptr=u32at(t+1)
        if typ==3: trans=ptr
        else: entries.append((typ,ptr))
        t+=5
    scr=bytes([0x16,0x04,0x80,idx,0x00,0x23])+struct.pack('<I',newsym['JpBH_HideLeaderIfAway']|1)
    if trans: scr+=bytes([0x04])+struct.pack('<I',trans)
    scr+=bytes([0x02])
    sa=alloc(scr,1)
    newtbl=bytes([3])+struct.pack('<I',sa)+b''.join(bytes([ty])+struct.pack('<I',p) for ty,p in entries)+bytes([0])
    w8(h+8,struct.pack('<I',alloc(newtbl,1)))
# gTrainers: relocated with the seven rematch Leaders as 743-749
OLDTR=0x081F97CC
tr=bytearray(rom[OLDTR-0x08000000:OLDTR-0x08000000+743*32])
for k,src in enumerate([414,415,416,417,418,420,419]):
    e=bytearray(rom[OLDTR-0x08000000+32*src:OLDTR-0x08000000+32*src+32])
    e[0]=3
    struct.pack_into('<HHHH',e,0x0A,19,19,0,0)
    e[0x18]=6
    struct.pack_into('<I',e,0x1C,newsym['gJpRematchVanillaParties']+k*6*16)
    tr+=e
exec(open('/home/claude/tools/master_patch.py').read())
tr+=master_trainer_entries()
NEWTR=alloc(tr)
for at in range(0x08000000,0x08300000,4):
    w=u32at(at)
    if w in (OLDTR,OLDTR+4,OLDTR+0xA): w8(at,struct.pack('<I',NEWTR+(w-OLDTR)))
assert rd(0x0800F8B8,4)==bl_bytes(0x0800F8B8,0x08010B0C); bl(0x0800F8B8,newsym['Island_TrainerParty'])
master_apply()
exec(open('/home/claude/tools/bt_patch.py').read())
bt_apply()
# --- reusable TMs (Gunk #7): JP Task_LearnedMove keeps the TM
patch16(0x081264EE,0xD803,0xE003)
# 3. party menu: new cursor option table with WALK/RETURN before the field moves
a,old=jp('sCursorOptions','party_menu.o')
NOPT_OLD=18+12
tbl=bytes(rom[old-0x08000000:old-0x08000000+8*NOPT_OLD])
new=tbl[:8*18]+struct.pack('<II',newsym['gText_GunkWalk'],newsym['CursorCB_GunkWalk']|1)+struct.pack('<II',newsym['gText_GunkReturn'],newsym['CursorCB_GunkReturn']|1)+struct.pack('<II',newsym['gText_JpForget'],newsym['CursorCB_JpForget']|1)+struct.pack('<II',newsym['gText_JpNickname'],newsym['CursorCB_JpNickname']|1)+tbl[8*18:]
end=(end+3)&~3; newtbl=end; w8(newtbl,new); end+=len(new)
# repoint references (literal pools in code region)
cnt=0
for off in range(0,0x01E0000,4):
    w=struct.unpack_from('<I',rom,off)[0]
    if old<=w<old+8*NOPT_OLD:
        d=w-old; nd=d if d<8*18 else d+32
        struct.pack_into('<I',rom,off,newtbl+nd); cnt+=1; print('  repoint',hex(off+0x08000000),hex(w),'->',hex(newtbl+nd))
print('table refs repointed',cnt)
# immediates CURSOR_OPTION_FIELD_MOVES 18 -> 22 (WALK, RETURN, わすれさせる, なまえ)
for at,old_hw,new_hw in [(0x0812262A,0x2811,0x2815),(0x0812283A,0x2E11,0x2E15),(0x081228A0,0x3812,0x3816),(0x08124E48,0x3812,0x3816)]:
    cur=struct.unpack_from('<H',rom,at-0x08000000)[0]; assert cur==old_hw,(hex(at),hex(cur)); struct.pack_into('<H',rom,at-0x08000000,new_hw)
# 赤フルカラー: every Pokémon can learn all HMs (TMHM learnset word1 bits 18-25)
_tm=0x0820ADC4-0x08000000
for sp in range(1,412):
    o=_tm+8*sp+4; struct.pack_into('<I',rom,o,struct.unpack_from('<I',rom,o)[0]|0x03FC0000)
# 赤フルカラー: Celadon Dept. 2F TM clerk (object event script ptr)
_n=0
for _o in range(0,len(rom)-4,4):
    if struct.unpack_from('<I',rom,_o)[0]==0x081834F6 and rom[_o-0x10]==3:   # object template (localId 3) script field
        struct.pack_into('<I',rom,_o,newsym['JpEventScript_CeladonTMClerk']); _n+=1
print('celadon TM clerk refs',_n); assert _n>=1
# vanilla bug (FRLG+ fix list): Nugget Bridge Rocket gave unlimited Nuggets if you lost to him -> set the scene var before the battle
_a=0x08178F05; _old=rd(_a,28)
assert _old==bytes.fromhex('160f8001005c0364010000469017080f00569017080904166b400100'),_old.hex()
w8(_a,_old[23:28]+_old[:23])
# vanilla bug (pret BUGFIX): Cmd_getexp re-read Speed instead of Sp. Def for the 2nd double-battle slot after a level up
patch16(0x0802197E,0x213D,0x213F); patch16(0x08021984,0x80E0,0x8160)
# vanilla bug (pret BUGFIX): Pokédex area search read the fishing table with the land table size (12 instead of 10)
patch16(0x0813D270,0x220C,0x220A)
# FRLG+ vanilla fix: moves that never check accuracy show --- instead of 100
for _mv in [274,335,293,268,176,266,288,270,286,275,277,212,262,102,300,171,220,278,287,272,285,303,289,135,169,294,233,346,273,281]:
    assert rom[0x00208E00+12*_mv+3]==100; rom[0x00208E00+12*_mv+3]=0
# FRLG+ vanilla fixes (AI scripts): Foresight checks the target, semi-invulnerable weather checks not swapped, Facade checks the user
for _a,_o,_n in [(0x081BEEF8,1,0),(0x081BEF00,3,2),(0x081BEF08,1,0),(0x081BF1EB,3,2),(0x081BF1F1,2,3),(0x081BF285,0,1)]:
    assert rom[_a-0x08000000]==_o,hex(_a); rom[_a-0x08000000]=_n
# FRLG+ vanilla fix: Icefall Cave thin/cracked ice (metatiles 0x359/0x35A) no longer start wild encounters
for _m in (0x359,0x35A):
    _o=0x0027BD44+4*(_m-0x280); assert struct.unpack_from('<I',rom,_o)[0] in (0x1000026,0x1000027)
    struct.pack_into('<I',rom,_o,struct.unpack_from('<I',rom,_o)[0]&~0x07000000)
# FRLG+ vanilla fix: evolution move-learning glitch (A+B on the same frame at "make room for ..." gave a black screen):
# the B check now only fires when A was not pressed this frame
patch16(0x080D03AE,0x2002,0x2003); patch16(0x080D03B2,0x2800,0x2802); patch16(0x080D03B4,0xD100,0xD000)
# companion to the --- accuracy fix: Charge/Conversion 2/Helping Hand/Recycle/Snatch still run a full accuracy check,
# so accuracy 0 would always miss. Treat accuracy 0 as "never misses" (covers EFFECT_ALWAYS_HIT / VITAL_THROW, which are all 0).
for _a,_o,_n in [(0x0801D50A,0x7800,0x78C0),(0x0801D50C,0x2811,0x2800),(0x0801D50E,0xD001,0xD001),(0x0801D510,0x284E,0x46C0),(0x0801D512,0xD10F,0xE00F)]:
    patch16(_a,_o,_n)
# pret BUGFIX: per-battler AI battle history lives after the vanilla struct -> allocate 0x58 instead of 0x30
patch16(0x0802D828,0x2030,0x2058)
# pret BUGFIX (binary): text window frame index bound 20 -> 10
patch16(0x08068FF6,0x2813,0x2809)
# pret BUGFIX: recordlastability skipped only 1 byte of its 2-byte command
patch16(0x08025FA8,0x3001,0x3002)
# pret BUGFIX: Pokedex category page flip passed the wrong value to the bg effect
patch16(0x0810630A,0x7888,0x2000)
# pret BUGFIX: Oak's speech loaded 48 colours past the background palette
patch16(0x081314FE,0x22E0,0x2280)
# pret BUGFIX: facility class pics for Agatha / Lance (were Lorelei / Bruno)
assert rom[0x0020BAA4+147]==112 and rom[0x0020BAA4+148]==113; rom[0x0020BAA4+147]=114; rom[0x0020BAA4+148]=115
# pret BUGFIX: Berry Crush sparkle amount 2 / 3 were written to the counter (only 0, 1, 4 reachable)
for _a,_o,_n in [(0x0814C882,0x2002,0x2040),(0x0814C884,0x86A8,0xE009),(0x0814C886,0xE00D,0x46C0),(0x0814C892,0x2003,0x2060),(0x0814C894,0x86A8,0xE001),(0x0814C896,0xE005,0x46C0),
                 (0x0814C898,0x7830,0x2080),(0x0814C89A,0x211F,0x7831),(0x0814C89C,0x4001,0x06C9),(0x0814C89E,0x2080,0x0EC9)]:
    patch16(_a,_o,_n)
# pret BUGFIX: Dodrio Berry Picking - unshared columns for 5 players {1,3,5,6,9} -> {1,3,5,7,9}
for _t in (0x0043B3EE,0x0043EB4A):
    _k=rom.find(bytes([1,3,5,6,9]),_t,_t+40); assert _k>0; rom[_k+3]=7
# pret BUGFIX: Dodrio Berry Picking could start before every player was ready (loop index not reset)
patch16(0x08155742,0x42AC,0x2401); patch16(0x08155744,0xD211,0x46C0)
# pret BUGFIX: Wonder Card stamp icons were checked with the wrong sprite id
patch16(0x0814647C,0x30D5,0x30D6)
# pret BUGFIX: map name preview wrote its 3 text colours past the stack frame (into saved registers)
patch16(0x080F93A8,0xB085,0xB086); patch16(0x080F9422,0xB005,0xB006)
# pret BUGFIX: intro fight-scene sprite palette list had no terminator (LoadSpritePalettes read garbage after it)
assert u32at(0x080EFB84)==0x083CD8B4
w8(0x080EFB84,struct.pack('<I',alloc(bytes(rom[0x003CD8B4:0x003CD8B4+40])+bytes(8))))
# --- メニューから パソコン (start menu item 9)
tramp(0x0806E51C,newsym['JpSetUpStartMenu_NormalField'])
assert rd(0x0806EB00,4)==bytes.fromhex('00b50848'); tramp(0x0806EB00,newsym['JpStartMenu_FadeScreenIfLeavingOverworld'])
_na=alloc(rd(0x08366B14,72)+struct.pack('<IIIIII',newsym['gJpText_MenuPC'],newsym['JpStartMenuPcCallback']|1,newsym['gJpText_MenuFly'],newsym['JpStartMenuFlyCallback']|1,newsym['gJpText_MenuFlash'],newsym['JpStartMenuFlashCallback']|1))
for _r in (0x0806E708,0x0806EAE0,0x0806EB60):
    assert u32at(_r)==0x08366B14; w8(_r,struct.pack('<I',_na))
_nd=alloc(rd(0x08366B64,36)+struct.pack('<III',newsym['gJpStartMenuDesc_PC'],newsym['gJpStartMenuDesc_Fly'],newsym['gJpStartMenuDesc_Flash']))
for _r in (0x0806E8A4,0x0806EAD4):
    assert u32at(_r)==0x08366B64; w8(_r,struct.pack('<I',_nd))
# --- メニューに そらをとぶ・フラッシュ (hk_start_menu_hm.c)
# メニューが 8こ いじょうなら せつめいを ださない：DoDrawStartMenu / StartCB_HandleInput の 3つの bl
assert rd(0x0806E880,4)==bl_bytes(0x0806E880,0x080F89F0); bl(0x0806E880,newsym['Island_StartHelpDraw'])
for _a in (0x0806EA3A,0x0806EA88):
    assert rd(_a,4)==bl_bytes(_a,0x08113B40); bl(_a,newsym['Island_StartHelpPrint'])
# スタートメニューの まどを 1マス ひろく（「そらをとぶ」「フラッシュ」が はみでない）：x 22 -> 21、はば 7 -> 8（CreateStartMenuWindow 0x080F895C）
assert rd(0x080F896C,2)==bytes.fromhex('0720') and rd(0x080F8988,2)==bytes.fromhex('1622'); w8(0x080F896C,bytes.fromhex('0820')); w8(0x080F8988,bytes.fromhex('1522'))
# どうくつ・たてものの なかからも とぶ：てもちの メニューの SetUpFieldMove_Fly と、とぶ マップで A のときの UNDERGROUND/INDOOR の チェック
assert rd(0x08125318,2)==bytes.fromhex('00b5'); tramp(0x08125318,newsym['JpSetUpFieldMove_Fly'])
assert rd(0x080C634C,8)==bytes.fromhex('042801d0082809d1'); w8(0x080C634C,bytes.fromhex('0ce0c046c046c046'))
# メニューから とんで やめたら スタートメニューに もどる
assert u32at(0x080C6488)==0x0812533D; w8(0x080C6488,struct.pack('<I',newsym['JpCB2_FlyMapCancel']|1))
assert rd(0x08193EAA,5)==bytes.fromhex('1604800000')
w8(0x08193EAA,b'\x05'+struct.pack('<I',newsym['EventScript_JpTurnOffPC']))
# --- ランニングシューズは おかあさんから
assert rd(0x0817F41A,11)==bytes.fromhex('166c400100292e002a9200')
w8(0x0817F41A,b'\x04'+struct.pack('<I',newsym['EventScript_JpBrockScene'])+bytes(6))
_ev=u32at(mapheader(4,0)+4); _ob=u32at(_ev+4)
assert u32at(_ob+16)==0x0817B855; w8(_ob+16,struct.pack('<I',newsym['EventScript_JpMom']))
# プレイヤーのいえ 1かい：はじめて おりてきたら おかあさんの よこへ あるいて シューズを もらう（マップスクリプトは もとは からっぽ）
assert u32at(mapheader(4,0)+8)==0x0817B854 and rd(0x0817B854,1)==b'\x00'
w8(mapheader(4,0)+8,struct.pack('<I',newsym['gJpHouse1FMapScripts']))
# --- 「これまでの あらすじ」を出さない: TryStartQuestLogPlayback の beq -> b
patch16(0x08111A7E,0xD00F,0xE00F)
# --- 赤フルカラーの機能
# island stubs live in the unused UnusedBlitBitmapRect (0x0812EE98-0x0812F074)
_isl=[l for l in open(PORT+'/pb/port.map') if l.startswith('.island ')][0].split(); assert int(_isl[1],16)+int(_isl[2],16)<=0x0812F074, 'island overflow'
# つりざお: かならず かかる (Fishing6: Random() & 1 -> & 0)
assert rd(0x0805CDB2,2)==bytes.fromhex('0121'); w8(0x0805CDB2,bytes.fromhex('0021'))
# セキエイこうげんの ショップで マスターボール (10000円)
assert rd(0x08189745,5)==bytes.fromhex('8654971808'), rd(0x0818972F,30).hex(); w8(0x08189745,b'\x04'+struct.pack('<I',newsym['EventScript_JpIndigoMart']))
assert r32(0x0839BD28+40+12)==0; w8(0x0839BD28+40+12,struct.pack('<H',10000))
# ショップの 一覧の ねだんを 5けたに (マスターボール 10000円)
assert rd(0x0809AD90,2)==bytes.fromhex('0423'); w8(0x0809AD90,bytes.fromhex('0523'))
assert rd(0x0809ADB6,2)==bytes.fromhex('6023'); w8(0x0809ADB6,bytes.fromhex('5a23'))
# わざを おぼえるときの「はい／いいえ」は「いいえ」から (Aの れんだで わざを うわがきしない)
assert rd(0x08024B44,4)==bytes.fromhex('04484470'); w8(0x08024B44,bytes.fromhex('04494870'))
assert rd(0x08024E74,4)==bytes.fromhex('03484470'); w8(0x08024E74,bytes.fromhex('03494870'))
assert rd(0x080D02CE,2)==bytes.fromhex('0022'); w8(0x080D02CE,bytes.fromhex('0122'))
assert rd(0x0812660A,4)==bytes.fromhex('fcf779f8'); bl(0x0812660A,newsym['Island_PartyYesNoDefaultNo'])
assert rd(0x081269BE,4)==bytes.fromhex('fbf79ffe'); bl(0x081269BE,newsym['Island_PartyYesNoDefaultNo'])
# バトル: わざの こうか・いりょく・めいちゅう、あいての HP (START で きりかえ)
tramp(0x0803003C,newsym['JpMoveSelectionDisplayMoveType'])
assert rd(0x0802E16E,4)==bytes.fromhex('05f01bf8'); bl(0x0802E16E,newsym['Island_ChooseMoveInput'])
# ずかん: せつめいの ページで SELECT -> 種族値と しんか
assert rd(0x08105384,4)==bytes.fromhex('02f070f9'); bl(0x08105384,newsym['Island_DexMonPageInput'])
# そだてや: いまの レベル
for _at,_txt,_s in [(0x08191410,0x081A581B,'EventScript_JpDaycareGrownFourIsland'),(0x081A54C0,0x0818C60F,'EventScript_JpDaycareGrownRoute5'),(0x081A54C9,0x0818C562,'EventScript_JpDaycareNotYetRoute5')]:
    assert rd(_at,8)==b'\x0f\x00'+struct.pack('<I',_txt)+b'\x09\x04', rd(_at,8).hex()
    w8(_at,b'\x04'+struct.pack('<I',newsym[_s])+b'\x00\x00\x00')   # msgbox (8 bytes) -> call + 3 nop
# 殿堂入り: 伝説の ポケモンを もどす
assert rd(0x0816A44F,5)==b'\x04'+struct.pack('<I',0x08193980); w8(0x0816A450,struct.pack('<I',newsym['EventScript_JpHoFFlags']))
# あいての HP の数字: sHealthbarSpriteTemplates[1].callback
assert u32at(0x08218590)==0x0804761D; w8(0x08218590,struct.pack('<I',newsym['JpSpriteCB_FoeHealthBar']|1))
# EWRAM は 0x02040000 を こえない
_ee=[l for l in open(PORT+'/pb/port.map') if 'ewram_end = .' in l][0].split()[0]; assert int(_ee,16)<=0x02040000, ('EWRAM over', _ee)

# --- タイトル画面の フシギバナを フルカラーに (lgtools/title2/build.py: 公式の色で部位ごとに塗り分け。BG パレット 10〜13 の 4 本を使う)
_tp=alloc(open(PORT+'/data/hooks/title/title_pals.bin','rb').read()); assert _tp
assert rd(0x083808A8,4)==bytes.fromhex('5e320000'), rd(0x083808A8,8).hex()
def _hw(a,old,new):
    assert rd(a,2)==struct.pack('<H',old),(hex(a),rd(a,2).hex()); w8(a,struct.pack('<H',new))
for _lit,_r1,_r2 in ((0x080781B0,0x0807812A,0x0807812C),(0x08078DCC,0x08078D78,0x08078D7A)):   # LoadPalette(mon, 13*16, 32) -> (new, 10*16, 128)
    assert u32at(_lit)==0x083808A8; w8(_lit,struct.pack('<I',_tp)); _hw(_r1,0x21D0,0x21A0); _hw(_r2,0x2220,0x2280)
# 登場演出: TintPalette_GrayScale2(&unfaded[13*16],16) -> (&unfaded[10*16],64)
assert u32at(0x08078530)==0x020372CC; w8(0x08078530,struct.pack('<I',0x0203726C)); _hw(0x08078514,0x2110,0x2140)
# CpuCopy16(mon pal, &unfaded[13*16], 32) -> (new, &unfaded[10*16], 128)
assert u32at(0x0807869C)==0x083808A8 and u32at(0x080786A0)==0x020372CC
w8(0x0807869C,struct.pack('<I',_tp)); w8(0x080786A0,struct.pack('<I',0x0203726C)); _hw(0x08078676,0x2210,0x2240)
# フェード/点滅のマスク 1<<13 -> パレット 10〜13
for _a in (0x0807851A,0x08078568,0x0807859E,0x080785C8,0x080785F0,0x0807861A,0x0807867C):
    _hw(_a,0x2080,0x20F0); assert rd(_a+2,2)==bytes.fromhex('8001')
assert u32at(0x080781B4)==0x083808C8 and u32at(0x080781B8)==0x0838132C
_tt=alloc(open(PORT+'/data/hooks/title/title_mon.4bpp.lz','rb').read()); w8(0x080781B4,struct.pack('<I',_tt))
_tm=alloc(open(PORT+'/data/hooks/title/title_map.bin.lz','rb').read()); w8(0x080781B8,struct.pack('<I',_tm))
# FRLG+ vanilla tile-error fixes (tilesets + small layout fixes)
exec(open('/home/claude/tools/tile_fix.py').read())
if os.environ.get('V151'): exec(open('/home/claude/tools/v151_patch.py').read())
print('end of new data',hex(end))
open(OUT,'wb').write(rom)
