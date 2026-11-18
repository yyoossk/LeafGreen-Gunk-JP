import sys, struct; sys.path.insert(0, "/home/claude/tools")
from story import *
import mkmon
K = sys.argv[1]; ST = {'jp': '/tmp/walkst/s20b_e4_jp.ss', 'fp': '/tmp/walkst/fp_new.ss'}[K]
g = Game(K, ST, rom='/home/claude/work/port151.gba' if K == 'jp' else None); g.run(10)
shots = []
def S(tag): f = f'/tmp/bt/{K}_{len(shots):03d}_{tag}.png'; g.shot(f); shots.append(f)
import os; os.makedirs('/tmp/bt', exist_ok=True)
for f in range(0x820, 0x828): g.setflag(f)
g.setflag(0x82C); g.setvar(0x4076, 5); g.setvar(0x407E, 3)
# the same 3 Lv50 mons in both: DRAGONITE / TYRANITAR / METAGROSS, stats 999
P = g.R['party']; own = g.peek(P, 100); otid = struct.unpack_from('<I', own, 4)[0]
team = [(149, (58, 85, 126, 89)), (248, (58, 85, 126, 89)), (376, (58, 85, 126, 89))]
data = b''
for i, (sp, mv) in enumerate(team):
    m = bytearray(mkmon.mon(sp, level=50, nick='ポケモン', pid=0x100 + i, otid=otid, moves=mv)); m[20:27] = own[20:27]
    m[84] = 50
    for off in (86, 88, 90, 92, 94, 96, 98): struct.pack_into('<H', m, off, 999)
    data += bytes(m)
for i, b in enumerate(data): g.cmd(f'poke {P + i:08X} {b:02X}')
g.cmd(f'poke {g.R["cnt"]:08X} 03')
g.setvar(0x4020, 250)
rec = []
print(g.teleport('VERMILION_CITY', 24, 32)); g.face('D'); S('dock')
g.tap('A'); g.run(40); S('sailor')
g.tap('A'); g.run(90); S('sailor')
g.tap('D'); g.run(10); S('menu'); g.tap('A'); g.run(60)
m0 = g.pos()[2:]
for i in range(60):
    g.tap('A'); g.run(40)
    if i % 6 == 0: S('ferry')
    if g.pos()[2:] != m0 and g.idle(): break
S('arrive'); print('arrive', g.pos())
arr = g.pos()[2:]
ws = g.events()['warps']; print('outside warps', ws)
# BT building door: the warp leading to another map with the smallest y
door = min(range(len(ws)), key=lambda i: ws[i]['y'])
g.warp_to(idx=door); g.run(120); S('lobby'); print('lobby', g.pos(), g.objects())
obs = [o for o in g.objects() if o[4] not in (254, 255)]
px0 = g.pos()[0]; rx, ry = min([o for o in obs if o[1] == px0] or obs, key=lambda o: o[2])[1:3]
print('receptionist', rx, ry, g.goto(rx, ry + 1)); g.hold('U', 20); g.run(10); g.face('U'); S('desk')
for i in range(20):
    if not g.in_overworld(): break
    g.tap('A'); g.run(40); S('desk')
g.run(60); S('party')
for k in 'AADAADAA': g.tap(k); g.run(30); S('choose')
g.tap('A'); g.run(60); S('confirm')
for i in range(40):
    if g.in_battle(): break
    g.tap('A'); g.run(40)
    if i % 3 == 0: S('go')
wins = 0
def bt_battle():
    # test cheat: the foe's HP is set to 1 at every command prompt (the user asked to cheat in the Battle Tower)
    n = 0
    while not g.in_overworld() and n < 400:
        n += 1
        if not g.in_battle(): g.tap('A'); continue
        f = g.u32(g.R['bcf'])
        if f == g.R['act']:
            for bi in (1, 3):
                a = g.R['bmons'] + 0x58 * bi + 0x28
                g.cmd(f'poke {a:08X} 01'); g.cmd(f'poke {a+1:08X} 00')
            a = g.R['bmons'] + 0x28; mx = g.u16(a + 4)        # and our HP back to full
            g.cmd(f'poke {a:08X} {mx & 0xFF:02X}'); g.cmd(f'poke {a+1:08X} {mx >> 8:02X}')
            g.tap('U'); g.tap('L'); g.tap('A')
        elif f == g.R['mv']:
            g.tap('U'); g.tap('L'); g.tap('A')
        else:
            g.tap('A')
        if n % 25 == 0: S('fight')
    for i in range(20):
        if g.idle(): break
        g.tap('A')
    return g.u8(g.R['outcome'])
for b in range(8):
    for i in range(80):
        if g.in_battle(): break
        g.tap('A'); g.run(20)
        if i % 8 == 0: S('between')
    if not g.in_battle(): break
    S('battle'); out = bt_battle(); wins += out == 1; S('after'); print('battle', b + 1, 'outcome', out, flush=True)
for i in range(30): g.tap('A'); g.run(30)
S('end'); print(K, 'wins', wins, g.pos()); g.save(f'/tmp/walkst/bt_end_{K}.ss'); g.close()
