# kit 21：殿堂入りの あとの わざおしえ マスター・わざマシン 50こ（リーフグリーン）
# python3 -I tutor_lg.py ROM STATE TAG early|shop|list|teach
import sys, struct; sys.path.insert(0, '/home/claude/tools')
from walker import *
import walker
rom, st, tag, mode = sys.argv[1:5]
OUT = '/tmp/t21/'
g = Game('jp', st, rom=rom); g.run(10)
P = g.R['party']
k = [0]
def shot(n): g.shot(f'{OUT}{tag}_{n}.png')
def downs(n, key='D'):
    for i in range(n): g.cmd(f'tap {key} 1'); g.run(6)
def runscript(data):
    buf = g.R['strbuf'] + 0x200
    for i, b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a, v in ((0x03000EB1, b'\x01'), (0x03000EB0, b'\x00'), (0x03000EB8, struct.pack('<I', buf)), (0x03000EA8, b'\x00')):
        for i, b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
def poke(a, data):
    for i, b in enumerate(data): g.cmd(f'poke {a+i:08X} {b:02X}')
def setlead(sp, lv):
    runscript(bytes([0x79]) + struct.pack('<HBHIIB', sp, lv, 0, 0, 0, 0) + b'\x02'); g.run(60)
    a = g.peek(P, 100); b = g.peek(P + 100, 100); poke(P, b); poke(P + 100, a)

if mode != 'early':
    g.setflag(0x82C)          # FLAG_SYS_GAME_CLEAR
    g.setflag(0x0EA, False)   # FLAG_JP_HIDE_MASTERS を けす（殿堂入りの あと）
g.teleport('CELADON_CITY_DEPARTMENT_STORE_2F', 4, 6); g.run(200)
objs = [(o['lid'], o['gfx'], o['x'], o['y']) for o in walker._events(g)['objs']]
master_visible = None
oe = g.peek(g.R['objs'], 0x24 * 16)
master_visible = any(oe[0x24*i] & 1 and struct.unpack_from('<hh', oe, 0x24*i + 0x10) == (4 + 7, 4 + 7) for i in range(16))
print(tag, 'master_on_map', master_visible)
if mode == 'early':
    shot('early')
elif mode == 'shop':
    g.teleport('CELADON_CITY_DEPARTMENT_STORE_2F', 2, 6); g.run(200); g.face('L'); g.run(10); g.tap('A')
    g.run(50); g.tap('A'); g.run(60); shot('shop0')
    for i in range(52): g.cmd('tap D 1'); g.run(4)
    g.run(20); shot('shop_end')
    for i in range(12): g.cmd('tap U 1'); g.run(4)
    g.run(20); shot('shop_mid')
else:
    setlead(6, 60)                       # リザードン Lv60（わざ 4つ）
    print(tag, 'moves_before', [struct.unpack_from('<H', g.peek(P, 100), 0)])
    g.teleport('CELADON_CITY_DEPARTMENT_STORE_2F', 4, 5); g.run(200); g.face('U'); g.run(10); g.tap('A')
    for i in range(3): g.run(40); g.tap('A')
    g.run(60); shot('list0')
    if mode == 'list':
        downs(17); g.run(10); shot('list_end')
        downs(14, 'U'); g.run(10); shot('list3')
        g.tap('B'); g.run(60); shot('bye'); g.tap('A'); g.run(60)
        print(tag, 'script_after_B', g.script_running())
    else:
        downs(3); g.run(10); shot('pick'); g.tap('A')     # のしかかり
        g.run(80); g.tap('A'); g.run(120); shot('party'); g.tap('A')
        g.run(80); shot('u00'); g.tap('A')             # あたらしく おぼえたい
        g.run(80); shot('u01'); g.tap('A')             # しかし 4つ
        g.run(80); shot('u02')                          # わすれさせますか？（はい／いいえ）
        g.tap('U'); g.run(20); shot('u03'); g.tap('A')  # はい
        g.run(150); shot('u04'); g.tap('A')            # わすれる わざ（1つめ）
        for i in range(5, 12):
            g.run(80); shot(f'u{i:02d}'); g.tap('A')
        g.run(60); shot('back')
        print(tag, 'list_again', g.script_running())
        g.tap('B'); g.run(60); g.tap('A'); g.run(60)
g.close()
