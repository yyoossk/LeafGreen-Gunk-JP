# FRLG+ RS Battle Tower: ROM-side patching (exec'd from patch_port.py after master_apply; uses its helpers)
import json
FP = '/home/claude/frlgplus/'
BTTS = '/home/claude/port/data/hooks/btts/'
JP_GROUP = 42                       # appended to gMapGroup_IndoorSevenIslandRoute (1 map) -> nums 1..5
JP_LAYOUTS, JP_NLAYOUTS = 0x0830E434, 383
JP_GENERAL, JP_BUILDING, JP_SILPHCO = 0x0829433C, 0x0829445C, 0x08294774
# Ruby/Sapphire Battle Tower BGM (extracted from JP Ruby by tools/gen_rs_music.py) -> new song id 347
import json as _json
_sb=open('/home/claude/port/sound/rs_btower/song.bin','rb').read(); _sj=_json.load(open('/home/claude/port/sound/rs_btower/song.json'))
_sa=alloc(_sb)
for _f in _sj['fixups']:
    struct.pack_into('<I',rom,_sa-0x08000000+_f,_sa+struct.unpack_from('<I',_sb,_f)[0])
_ST=0x0846354C; _NS=347
_nt=alloc(bytes(rom[_ST-0x08000000:_ST-0x08000000+8*_NS])+struct.pack('<IHH',_sa+_sj['header'],*_sj['ms']))
for _r in (0x081C0C70,0x081C0CA4,0x081C0CF0,0x081C0D44,0x081C0D78):
    assert u32at(_r)==_ST; w8(_r,struct.pack('<I',_nt))
MUS_BT = _NS
MAPSEC_BATTLE_FRONTIER = 0x3A

def bt_apply():
    # --- FRLG+'s extra General metatile 0x229 (uses the outside tileset's tiles)
    gm = u32at(JP_GENERAL + 12); ga = u32at(JP_GENERAL + 20)
    assert rd(gm + 0x229 * 16, 16) == b'\0' * 16
    fm = open(FP + 'data/tilesets/primary/general/metatiles.bin', 'rb').read(); fa = open(FP + 'data/tilesets/primary/general/metatile_attributes.bin', 'rb').read()
    w8(gm + 0x229 * 16, fm[0x229 * 16:0x22A * 16]); w8(ga + 0x229 * 4, fa[0x229 * 4:0x22A * 4])
    # --- layouts 384..388
    LAY = [('out', 29, 30, JP_GENERAL, newsym['gJpTileset_BattleFrontierOutsideEast']),
           ('lobby', 14, 10, JP_BUILDING, newsym['gJpTileset_BattleFrontier']),
           ('elev', 5, 8, JP_BUILDING, JP_SILPHCO),
           ('corr', 17, 5, JP_BUILDING, newsym['gJpTileset_BattleFrontier']),
           ('room', 10, 10, JP_BUILDING, newsym['gJpTileset_BattleFrontier'])]
    layptrs = []
    for short, w, h, prim, sec in LAY:
        mp = open(BTTS + 'lay_%s_map.bin' % short, 'rb').read(); bd = open(BTTS + 'lay_%s_border.bin' % short, 'rb').read()
        assert len(mp) == 2 * w * h
        layptrs.append(alloc(struct.pack('<iiIIIIBBxx', w, h, alloc(bd), alloc(mp), prim, sec, 2, 2)))
    newtbl = alloc(rd(JP_LAYOUTS, 4 * JP_NLAYOUTS) + b''.join(struct.pack('<I', p) for p in layptrs))
    assert u32at(0x08054A30) == JP_LAYOUTS
    w8(0x08054A30, struct.pack('<I', newtbl))
    # --- object sprites: gfx 170 Scott (pink NPC palette), 171 Sudowoodo (green), copies of JP infos with FRLG+ pixels
    GP = 0x0835F5F8
    def base_with(tag):
        for gid in range(152):
            info = rd(u32at(GP + 4 * gid), 36)
            t, slot = struct.unpack_from('<H', info, 2)[0], info[12] & 0xF
            if t == tag and struct.unpack_from('<hh', info, 8) == (16, 32) and struct.unpack_from('<H', info, 6)[0] == 256:
                return bytearray(info)
        raise Exception('no base for %x' % tag)
    extra = []
    for sym, tag, frames in [('gJpBTOwScott', 0x1104, [0, 1, 2, 3, 4, 5, 6, 7, 8, 0]), ('gJpBTOwSudowoodo', 0x1105, [0, 0, 1, 0, 0, 0, 0, 1, 2, 0])]:
        info = base_with(tag)
        tbl = alloc(b''.join(struct.pack('<IHxx', newsym[sym] + 256 * f, 256) for f in frames))
        struct.pack_into('<I', info, 28, tbl)
        extra.append(alloc(bytes(info)))
    w8(newsym['gJpMasterGfxPtrs'] + 4 * 10, b''.join(struct.pack('<I', a) for a in extra))
    # --- the five maps
    def events(objs, warps, bgs):
        o = b''.join(objtmpl(i + 1, *ob) for i, ob in enumerate(objs))
        wp = b''.join(struct.pack('<hhBBBB', x, y, 0, wid, mn, mg) for x, y, wid, mg, mn in warps)
        bg = b''.join(bgev(x, y, kind, s) for x, y, kind, s in bgs)
        return struct.pack('<BBBBIIII', len(objs), len(warps), 0, len(bgs), alloc(o) if o else 0, alloc(wp) if wp else 0, 0, alloc(bg) if bg else 0)
    S = lambda n: newsym[n]
    G = JP_GROUP
    maps = [
        # name, layout#, scripts, events, mapType, bike, flags(escape|run<<1|showname<<2), battleScene
        ('out', 0, 'JpBT_Outside_MapScripts', events(
            [(19, 9, 10, 3, 0x02, 1, 1, S('JpBT_Outside_EventScript_Boy'), 0),
             (42, 11, 14, 3, 0x02, 1, 1, S('JpBT_Outside_EventScript_Cooltrainer'), 0),
             (20, 19, 11, 3, 0x02, 1, 1, S('JpBT_Outside_EventScript_BugCatcher'), 0),
             (62, 19, 25, 3, 0x07, 0, 0, S('JpBT_Outside_EventScript_Sailor'), 0),
             (108, 19, 27, 3, 0x09, 0, 0, 0, 0),
             (35, 8, 12, 3, 0x08, 0, 0, S('JpBT_Outside_EventScript_OldWoman'), 0),
             (171, 8, 13, 3, 0x08, 0, 0, S('JpBT_Outside_EventScript_Sudowoodo'), 0x0ED)],
            [(14, 8, 0, G, 2)],
            [(16, 13, 0, S('JpBT_Outside_EventScript_Sign'))]), 1, 1, 0x06, 0),
        ('lobby', 1, 'JpBT_Lobby_MapScripts', events(
            [(65, 6, 5, 3, 0x08, 0, 0, S('JpBT_Lobby_EventScript_Receptionist'), 0),
             (47, 12, 3, 3, 0x08, 0, 0, S('JpBT_Lobby_EventScript_Worker'), 0),
             (42, 10, 8, 3, 0x02, 1, 1, S('JpBT_Lobby_EventScript_Cooltrainer'), 0),
             (19, 1, 2, 3, 0x02, 1, 1, S('JpBT_Lobby_EventScript_Boy'), 0),
             (170, 7, 6, 3, 0x09, 0, 0, S('JpBT_Lobby_EventScript_Scott'), 0x0EE)],
            [(6, 8, 0, G, 1), (6, 1, 0, G, 5)],
            [(3, 5, 1, S('JpBT_Lobby_EventScript_Records'))]), 8, 0, 0x02, 0),
        ('elev', 2, 'JpBT_Elevator_MapScripts', events([(65, 2, 5, 3, 0x07, 0, 0, 0, 0)], [], []), 8, 0, 0x02, 0),
        ('corr', 3, 'JpBT_Corridor_MapScripts', events([(65, 9, 2, 3, 0x09, 0, 0, 0, 0)], [], []), 8, 0, 0x02, 0),
        ('room', 4, 'JpBT_Room_MapScripts', events(
            [(240, 5, 1, 3, 0x08, 0, 0, 0, 0x0EF), (65, 1, 7, 3, 0x0A, 0, 0, 0, 0)],
            [(5, 8, 2, G, 2), (6, 8, 2, G, 2)], []), 8, 0, 0x02, 8),
    ]
    hdrs = []
    for name, li, scr, ev, mtype, bike, flags, scene in maps:
        hdrs.append(alloc(struct.pack('<IIIIHHBBBBBBbB', layptrs[li], alloc(ev), S(scr), 0, MUS_BT, JP_NLAYOUTS + 1 + li,
                                       MAPSEC_BATTLE_FRONTIER, 0, 0, mtype, bike, flags, 0, scene)))
    gp = u32at(MAPGROUPS + 4 * G)
    w8(MAPGROUPS + 4 * G, struct.pack('<I', alloc(rd(gp, 4) + b''.join(struct.pack('<I', h) for h in hdrs))))
    # --- Seagallop: destination 12 = the Battle Tower dock (19, 24)
    SEAG = 0x0842FDF8
    assert u32at(0x08147324) == SEAG and rd(0x081472BC, 2) == b'\x0a\x28'
    dst = rd(SEAG, 44) + b'\x00\x00\x00\x00' + bytes([G, 1, 19, 24])
    w8(0x08147324, struct.pack('<I', alloc(dst)))
    w8(0x081472BC, b'\x0c\x28')
    # --- multichoice lists 64 (Lv50 / Open Level / Quit) and 65 (Sevii / Battle Tower / Quit)
    MC = 0x083A0BAC
    mc = alloc(rd(MC, 64 * 8) + struct.pack('<IBxxx', newsym['gJpBTMultichoiceLevels'], 3) + struct.pack('<IBxxx', newsym['gJpBTMultichoiceFerry'], 3))
    for at in (0x0809C480, 0x0809C954):
        assert u32at(at) == MC
        w8(at, struct.pack('<I', mc))
    MCW = 0x083A0DAC                    # JP multichoice widths (tiles), one byte per list
    assert u32at(0x0809C4D8) == MCW and rd(0x0809C472, 2) == b'\x3f\x2d'
    w8(0x0809C4D8, struct.pack('<I', alloc(rd(MCW, 64) + bytes([11, 9]), 1)))
    w8(0x0809C472, b'\x41\x2d')
    # --- Vermilion: the ferry sailor's Rainbow Pass branch asks Sevii Islands / Battle Tower first
    for at in (0x081719D4, 0x08171C2B):
        assert rd(at, 7) == bytes.fromhex('21764005000604') and u32at(at + 7) == 0x081719F4
        w8(at + 7, struct.pack('<I', newsym['JpBT_EventScript_FerryRainbow']))
    w8(newsym['JpBT_FerryRainbowOriginal'], struct.pack('<I', 0x081719F4))
    # vanilla bug (FRLG+ fixes it): a Battle Tower trainer's name isn't copied into the battle message
    assert rd(0x080D914E, 10) == bytes.fromhex('6846') + bl_bytes(0x080D9150, 0x080E7118) + bytes.fromhex('4be10000')
    w8(0x080D9154, bytes.fromhex('6c46') + struct.pack('<H', 0xE000 | ((0x080D93EE - (0x080D9156 + 4)) >> 1)))
    print('battle tower: maps (42,1-5), layouts %d-%d' % (JP_NLAYOUTS + 1, JP_NLAYOUTS + 5))
