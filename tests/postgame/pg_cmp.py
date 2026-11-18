import sys, struct, os; sys.path.insert(0, "/home/claude/tools")
from story import *
import mkmon
K = sys.argv[1]
ST = {'jp': '/tmp/walkst/s21_postgame_jp.ss', 'fp': '/tmp/walkst/fp_new.ss'}[K]
g = Game(K, ST, rom='/home/claude/work/port151.gba' if K == 'jp' else None); g.run(10)
os.makedirs('/tmp/pg', exist_ok=True)
def cheat_battle(log=None):
    n = 0
    while not g.in_overworld() and n < 400:
        n += 1
        if not g.in_battle(): g.tap('A'); continue
        f = g.u32(g.R['bcf'])
        if f == g.R['act']:
            for bi in (1, 3):
                a = g.R['bmons'] + 0x58 * bi + 0x28; g.cmd(f'poke {a:08X} 01'); g.cmd(f'poke {a+1:08X} 00')
            a = g.R['bmons'] + 0x28; mx = g.u16(a + 4); g.cmd(f'poke {a:08X} {mx & 0xFF:02X}'); g.cmd(f'poke {a+1:08X} {mx >> 8:02X}')
            g.tap('U'); g.tap('L'); g.tap('A')
        elif f == g.R['mv']: g.tap('U'); g.tap('L'); g.tap('A')
        else: g.tap('A')
        if log is not None and n % 30 == 0: log.append(g.snap('b'))
    for i in range(20):
        if g.idle(): break
        g.tap('A')
    return g.u8(g.R['outcome'])
g.battle = cheat_battle
for f in list(range(0x820, 0x828)) + [0x82C, 0x840]: g.setflag(f)
g.setvar(0x4076, 6); g.setvar(0x4020, 250)
# Pokédex: all 151 seen + caught (for the diploma / ticket)
sb = g.sb1(); sb2 = g.u32(g.R['sb1'] + 4)
for base in (sb2 + 0x28, sb2 + 0x5C, sb + 0x5F8, sb + 0x3A18):
    for i in range(19): g.cmd(f'poke {base + i:08X} FF')
    g.cmd(f'poke {base + 18:08X} 7F')
# party: MUK (for the Celadon Master Trainer) + strong mons
P = g.R['party']; own = g.peek(P, 100); otid = struct.unpack_from('<I', own, 4)[0]
data = b''
for i, (sp, mv) in enumerate([(88, (58, 85, 126, 89)), (149, (58, 85, 126, 89)), (248, (58, 85, 126, 89))]):
    m = bytearray(mkmon.mon(sp, level=100, nick='ポケモン', pid=0x200 + i, otid=otid, moves=mv)); m[20:27] = own[20:27]; data += bytes(m)
for i, b in enumerate(data): g.cmd(f'poke {P + i:08X} {b:02X}')
g.cmd(f'poke {g.R["cnt"]:08X} 03'); g.boost()
rec = []
def T(label, *a):
    try: r = g.interact(*a, label, rec, key='A')
    except Exception as e: r = repr(e)
    print(K, label, r, g.pos(), flush=True)
def TP(name, x, y):
    for t in range(4):
        for i in range(15):
            if g.in_overworld() and g.idle(): break
            g.tap('B'); g.run(20)
        p = g.teleport(name, x, y)
        if p[2:] == mapid(name): break
        rec.append((f'tp retry {name}', [g.snap('tp')]))
    print(K, 'tp', name, p, flush=True)
TP('PALLET_TOWN', 10, 9); T('master guide', 10, 7)
TP('PALLET_TOWN_PROFESSOR_OAKS_LAB', 6, 6); T('oak', 6, 3)
TP('CELADON_CITY_CONDOMINIUMS_3F', 3, 10); g.step('U'); g.face('U'); g.tap('A'); g.run(40); sh=[]
for i in range(40):
    if i % 2 == 0: sh.append(g.snap('d'))
    if g.idle(): break
    g.tap('A' if g.cb2() != g.R['owcb'] else 'B'); g.run(40)
rec.append(('designer', sh)); print(K, 'designer', g.idle(), 'ticket', g.getflag(0x2A8), flush=True)
T('title giver', 6, 12)
TP('CELADON_CITY', 28, 21); T('master muk', 28, 19)
TP('CELADON_CITY_CONDOMINIUMS_3F', 5, 12); T('title giver2', 6, 12)
TP('SEVEN_ISLAND', 10, 10); T('mailbox', 10, 9)
TP('SEVEN_ISLAND_HOUSE_ROOM1', 4, 6); T('old woman', 4, 4); T('spearow', 9, 6); T('old woman2', 4, 4)
TP('SEVEN_ISLAND_HOUSE_ROOM2', 4, 5); g.explore(rec)
TP('VERMILION_CITY', 24, 32); g.face('D'); g.tap('A'); g.run(60); rec.append(('ferry menu', [g.snap('f')]))
for i in range(3): g.tap('A'); g.run(60); rec[-1][1].append(g.snap('f'))
for i in range(6): g.tap('D'); g.run(10)
rec[-1][1].append(g.snap('f'))
import json
json.dump(rec, open(f'/tmp/pg/{K}.json', 'w'))
g.save(f'/tmp/walkst/pg_end_{K}.ss'); g.close()
