# FRLG+ Master Trainers: ROM-side patching (exec'd from patch_port.py; uses its rom/alloc/newsym helpers)
import json, subprocess, os
MJ = json.load(open('/home/claude/work/master_place.json'))
JP_MASTER_BASE = 750
FRLGP_GFX = '/home/claude/port/graphics/master_trainers/'
GBAGFX = '/home/claude/pret/tools/gbagfx/gbagfx'
TMP = '/home/claude/work/mastergfx/'
os.makedirs(TMP, exist_ok=True)

def jpstr(s, n):
    import re
    enc = {}
    for line in open('/home/claude/port/charmap.txt', encoding='utf-8'):
        m = re.match(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$", line.split('@')[0].strip())
        if m: enc.setdefault(m.group(1), int(m.group(2), 16))
    b = bytes(enc[c] for c in s) + b'\xff'
    assert len(b) <= n, s
    return b + b'\x00' * (n - len(b))

def gfx(png, out, *args):
    subprocess.check_call([GBAGFX, png, out] + list(args))
    return open(out, 'rb').read()

def lz(path_in, data):
    open(path_in, 'wb').write(data)
    subprocess.check_call([GBAGFX, path_in, path_in + '.lz'])
    return open(path_in + '.lz', 'rb').read()

def master_trainer_entries():
    """151 Master Trainer entries (ids 750-900) + Oak (901) for the relocated gTrainers"""
    out = b''
    for sp in range(1, 152):
        t = MJ['trainers'].get(str(sp))
        e = bytearray(32)
        if t is None:            # no-battle Masters: an unused dummy
            e[1] = 82; e[3] = 107; e[4:10] = jpstr('ー', 6)
            struct.pack_into('<I', e, 0x1C, DUMMY_PARTY); e[0x18] = 1
        else:
            e[0] = 0; e[1] = t['cls']; e[2] = t['music']; e[3] = t['pic'] if 'newpic' not in SKIP else 100
            e[4:10] = jpstr(t['name'], 6)
            struct.pack_into('<I', e, 0x14, 7)
            e[0x18] = 1
            struct.pack_into('<I', e, 0x1C, alloc(struct.pack('<HBxHxx', 0, 50, SPECIES_NUM[t['species']])))
        out += bytes(e)
    e = bytearray(32)
    e[1] = 97; e[2] = 0; e[3] = 132; e[4:10] = jpstr('オーキド', 6)
    struct.pack_into('<I', e, 0x14, 7 | 256); e[0x18] = 6
    struct.pack_into('<I', e, 0x1C, alloc(b''.join(struct.pack('<HBxHxx', 0, 80, s) for s in (128, 103, 59, 130, 26, 143))))
    out += bytes(e)
    return out

import re as _re
SPECIES_NUM = {k: int(v) for k, v in _re.findall(r'#define (SPECIES_\w+)\s+(\d+)', open('/home/claude/pret/include/constants/species.h').read())}
DUMMY_PARTY = alloc(struct.pack('<HBxHxx', 0, 50, 132))

def master_apply():
    # --- trainer front pics 148-158 (JP tables relocated with 11 more entries)
    PICS, PALS, COORDS, ANIMS = 0x081F4354, 0x081F47F4, 0x081F4104, 0x081F3EB4
    assert struct.unpack_from('<HH', rom, PICS + 8 * 147 + 4 - 0x08000000) == (2048, 147)
    pics = bytearray(rd(PICS, 148 * 8)); pals = bytearray(rd(PALS, 148 * 8)); coords = bytearray(rd(COORDS, 148 * 4)); anims = bytearray(rd(ANIMS, 148 * 4))
    FN = dict(BEAUTY='master_beauty', BIRD_KEEPER='master_bird_keeper', BLACK_BELT='master_black_belt', BUG_CATCHER='master_bug_catcher',
              COOLTRAINER_M='master_cool_trainer_m', HIKER='master_hiker', LASS='master_lass', PSYCHIC_M='master_psychic_m',
              SCIENTIST='master_scientist', YOUNGSTER='master_youngster', SWIMMER='master_swimmer')
    BASEPIC = dict(BEAUTY=98, BIRD_KEEPER=104, BLACK_BELT=105, BUG_CATCHER=83, COOLTRAINER_M=110, HIKER=90, LASS=84, PSYCHIC_M=100,
                   SCIENTIST=107, YOUNGSTER=82, SWIMMER=99)
    for i, n in enumerate(MJ['newpics']):
        pid = 148 + i
        png = FRLGP_GFX + 'front_pics/%s_front_pic.png' % FN[n]
        tiles = gfx(png, TMP + n + '.4bpp'); assert len(tiles) == 2048
        pal = gfx(png, TMP + n + '.gbapal')
        pics += struct.pack('<IHH', alloc(lz(TMP + n + '.4bpp', tiles)), 2048, pid)
        pals += struct.pack('<IHH', alloc(lz(TMP + n + '.gbapal', pal)), pid, 0)
        coords += rd(COORDS + 4 * BASEPIC[n], 4)
        anims += rd(ANIMS + 4 * BASEPIC[n], 4)
    for old, new in ([] if 'pics' in SKIP else [(PICS, alloc(bytes(pics))), (PALS, alloc(bytes(pals))), (COORDS, alloc(bytes(coords))), (ANIMS, alloc(bytes(anims)))]):
        c = 0
        for at in range(0x08000000, 0x08300000, 4):
            w = u32at(at)
            if old <= w < old + 4 and (w - old) % 2 == 0:
                w8(at, struct.pack('<I', new + (w - old))); c += 1
        print('trainer pic table %08X -> %08X refs %d' % (old, new, c))
    # --- overworld sprites: gfx 160-169 = copies of Lass (blue NPC palette) / Hiker (white) with FRLG+'s pixels
    GP = 0x0835F5F8
    OWN = ['beauty', 'bird_keeper', 'blackbelt', 'bug_catcher', 'cooltrainer_m', 'hiker', 'lass', 'psychic_m', 'scientist', 'youngster']
    WHITE = {'bird_keeper', 'blackbelt', 'bug_catcher', 'hiker', 'scientist'}
    infos = []
    for n in OWN:
        base = u32at(GP + 4 * (56 if n in WHITE else 22))
        info = bytearray(rd(base, 36))
        px = gfx(FRLGP_GFX + 'people/master_%s.png' % n, TMP + 'ow_' + n + '.4bpp', '-mwidth', '2', '-mheight', '4')
        assert len(px) == 2560, (n, len(px))
        pa = alloc(px)
        tbl = alloc(b''.join(struct.pack('<IHxx', pa + 256 * k, 256) for k in range(10)))
        struct.pack_into('<I', info, 28, tbl)
        infos.append(alloc(bytes(info)))
    w8(newsym['gJpMasterGfxPtrs'], b''.join(struct.pack('<I', a) for a in infos))
    # --- the trainers on the maps (object flag FLAG_JP_HIDE_MASTERS 0x0EA)
    bymap = {}
    for p in MJ['place']: bymap.setdefault((p['g'], p['n']), []).append(p)
    extra = {(3, 0): [('obj', 18, 10, 7, 3, 8, newsym['JpMaster_EventScript_Guide'], 0x0EA)],
             (10, 9): [('obj', 42, 6, 12, 3, 9, newsym['JpMaster_EventScript_TitleGiver'], 0)]}
    for key in set(bymap) | set(extra):
        g, n = key
        h = mapheader(g, n); ev = u32at(h + 4)
        cnt = list(rd(ev, 4)); no = cnt[0]
        objs = rd(u32at(ev + 4), 24 * no) if no else b''
        new = []
        for p in bymap.get(key, []):
            new.append((p['gfx'], p['x'], p['y'], p['elev'], p['mt'], newsym['gJpMasterScripts'] and u32at(newsym['gJpMasterScripts'] + 4 * p['sp']), 0x0EA))
        for e in extra.get(key, []):
            new.append(e[1:])
        for k, (gid, x, y, el, mt, scr, fl) in enumerate(new):
            assert scr, key
            objs += objtmpl(no + 1 + k, gid, x, y, el, mt, 0, 0, scr, fl)
        cnt[0] = no + len(new)
        assert cnt[0] <= 64
        w8(h + 4, struct.pack('<I', alloc(bytes(cnt) + struct.pack('<IIII', alloc(objs), u32at(ev + 8), u32at(ev + 12), u32at(ev + 16)))))
    print('master trainers placed on', len(bymap), 'maps')
    # --- Pewter City / Route 2 ledges (ON_LOAD, chained to the map's own ON_LOAD script if any)
    for (g, n), scr, nxt in [((3, 2), 'JpMaster_MapScript_PewterLedge', 'JpMaster_PewterOnLoadNext'), ((3, 20), 'JpMaster_MapScript_Route2Ledge', 'JpMaster_Route2OnLoadNext')]:
        h = mapheader(g, n); t = u32at(h + 8); entries = []; old = None
        while rom[t - 0x08000000] != 0:
            typ = rom[t - 0x08000000]; ptr = u32at(t + 1)
            if typ == 1: old = ptr
            else: entries.append((typ, ptr))
            t += 5
        if old: w8(newsym[nxt], struct.pack('<I', old))
        else: w8(newsym[nxt] - 1, b'\x02')
        newtbl = bytes([1]) + struct.pack('<I', newsym[scr]) + b''.join(bytes([ty]) + struct.pack('<I', p) for ty, p in entries) + b'\x00'
        w8(h + 8, struct.pack('<I', alloc(newtbl, 1)))
    # --- Professor Oak: the lab's Oak object runs the superboss check first
    h = mapheader(4, 3); ev = u32at(h + 4); ob = u32at(ev + 4) + 24 * 3
    assert rom[ob - 0x08000000] == 4, rom[ob - 0x08000000]
    w8(newsym['JpMaster_OakOriginalScript'], struct.pack('<I', u32at(ob + 16)))
    w8(ob + 16, struct.pack('<I', newsym['JpMaster_EventScript_Oak']))
    # --- battle: no trainer flag, no items, no prize money
    assert rd(0x0807F73C, 4) == bytes.fromhex('0449a022')
    tramp(0x0807F73C, newsym['JpGetTrainerAFlag'])
    assert rd(0x08013B64, 4) == bytes.fromhex('0e490840'), rd(0x08013B64, 4).hex()
    bl(0x08013B64, newsym['Island_MasterItemBlock'])
    ORIGWON = 0x081BC343
    assert u32at(0x08014EA8) == ORIGWON
    master = bytes.fromhex('104101' '5301' '3a' '100c00' '124000' '3e')
    # jumpifhalfword GT opponent 749 -> chk2 ; goto original ; chk2: jumpifhalfword LT opponent 901 -> master ; goto original ; master...
    base = alloc(b'\x00' * (34 + len(master)), 1)
    chk2 = base + 17; mst = base + 34
    s = (b'\x2a\x02' + struct.pack('<IHI', 0x020385E2, JP_MASTER_BASE - 1, chk2) + b'\x28' + struct.pack('<I', ORIGWON) +
         b'\x2a\x03' + struct.pack('<IHI', 0x020385E2, JP_MASTER_BASE + 151, mst) + b'\x28' + struct.pack('<I', ORIGWON) + master)
    assert len(s) == 34 + len(master)
    w8(base, s)
    w8(0x08014EA8, struct.pack('<I', base))
    # losing: no white-out (CB2_EndTrainerBattle) and no lost-battle messages / prize money (HandleEndTurn_BattleLost)
    assert rd(0x0807FBAC, 4) == bl_bytes(0x0807FBAC, 0x0807F754)
    bl(0x0807FBAC, newsym['Island_MasterEndDefeated'])
    ORIGLOST = 0x081BC35A
    assert u32at(0x08014FC8) == ORIGLOST
    base = alloc(b'\x00' * 35, 1)
    s = (b'\x2a\x02' + struct.pack('<IHI', 0x020385E2, JP_MASTER_BASE - 1, base + 17) + b'\x28' + struct.pack('<I', ORIGLOST) +
         b'\x2a\x03' + struct.pack('<IHI', 0x020385E2, JP_MASTER_BASE + 151, base + 34) + b'\x28' + struct.pack('<I', ORIGLOST) + b'\x3e')
    w8(base, s)
    w8(0x08014FC8, struct.pack('<I', base))
