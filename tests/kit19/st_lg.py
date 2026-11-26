# kit 19：あいての じょうたい アイコンで HP の 数字の 行に 色が のびない か（リーフグリーン）
# python3 -I st_lg.py ROM STATE TAG start STATUS        バトルの さいしょから あいて・じぶんが じょうたい
# python3 -I st_lg.py ROM STATE TAG mid SPECIES LV STSLOT ATKSLOT   とちゅうで じょうたいに して、そのあと HP が へる
# python3 -I st_lg.py ROM STATE TAG trainer             トレーナー戦で やけどの ポケモンが 出てくる
import sys, struct; sys.path.insert(0, '/home/claude/tools')
from walker import *
rom, st, tag, mode = sys.argv[1:5]
OUT = '/tmp/st19/'
g = Game('jp', st, rom=rom); g.run(10)
P = g.R['party']; E = P - 600

def runscript(data):
    buf = g.R['strbuf'] + 0x200
    for i, b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a, v in ((0x03000EB1, b'\x01'), (0x03000EB0, b'\x00'), (0x03000EB8, struct.pack('<I', buf)), (0x03000EA8, b'\x00')):
        for i, b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
    return buf

def poke(a, data):
    for i, b in enumerate(data): g.cmd(f'poke {a+i:08X} {b:02X}')

def setlead(sp, lv):
    runscript(bytes([0x79]) + struct.pack('<HBHIIB', sp, lv, 0, 0, 0, 0) + b'\x02'); g.run(60)
    a = g.peek(P, 100); b = g.peek(P + 100, 100)
    poke(P, b); poke(P + 100, a)
    poke(P + 0x56, struct.pack('<H', 999)); poke(P + 0x58, struct.pack('<H', 999))

def wild():
    runscript(bytes([0xB6]) + struct.pack('<HBH', 19, 30, 0) + bytes([0xB7, 0x02]))

def act():
    for i in range(400):
        if g.in_battle() and g.u32(g.R['bcf']) == g.R['act']: return True
        if i > 60 and not g.in_battle(): return False
        g.tap('B'); g.run(10)
    return False

k = 0
def sh():
    global k
    g.run(20); g.shot(f'{OUT}{tag}_{k}.png'); k += 1

def fight(slot):
    g.cmd('tap U 1'); g.run(4); g.cmd('tap L 1'); g.run(4); g.tap('A'); g.run(20)
    g.cmd('tap U 1'); g.run(4); g.cmd('tap L 1'); g.run(4)
    if slot & 1: g.cmd('tap R 1'); g.run(4)
    if slot & 2: g.cmd('tap D 1'); g.run(4)
    g.tap('A'); g.run(10)

if mode == 'start':
    v = {'brn': 0x10, 'psn': 0x08, 'par': 0x40, 'slp': 0x03, 'frz': 0x20, 'tox': 0x80}[sys.argv[5]]
    runscript(bytes([0xB6]) + struct.pack('<HBH', 19, 4, 0) + b'\x02'); g.run(5)
    for base in (E, P): poke(base + 0x50, struct.pack('<I', v))
    runscript(bytes([0xB7, 0x02]))
    for i in range(40):
        g.run(30)
        if g.in_battle(): break
    act(); sh()
    fight(0)
    if act(): sh()
elif mode == 'mid':
    sp, lv, sts, atk = map(int, sys.argv[5:9])
    setlead(sp, lv); wild()
    for turn in range(6):
        if not act(): break
        sh()
        fight(sts if turn < 2 else atk)
    if act(): sh()
elif mode == 'trainer':
    setlead(150, 100)
    tid = 415                     # カスミ（ヒトデマン・スターミー）
    sb1 = g.u32(0x03004FA8); f = 0x500 + tid; a = sb1 + 0xEE0 + f // 8
    poke(a, bytes([g.u8(a) & ~(1 << (f % 8)) & 0xFF]))
    buf = g.R['strbuf'] + 0x200
    runscript(bytes([0x5C, 3]) + struct.pack('<HH', tid, 0) + struct.pack('<I', buf + 20) + b'\x02' + b'\x00' * 9 + b'\xFF')
    for i in range(60):
        g.run(30)
        if g.in_battle(): break
        g.tap('A')
    poke(E + 100 + 0x50, struct.pack('<I', 0x10))   # 2ひきめを やけどに
    for turn in range(4):
        if not act(): break
        sh(); fight(0)
g.close()
print(tag, k)
