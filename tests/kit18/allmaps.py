# でるポケモン：野生の ポケモンが でる 全マップで、スタートメニュー（field）か ずかん（dex）の 表示を 撮る
# python3 -I allmaps.py ROM STATE field|dex TAG   -> /tmp/am/TAG_*.png, /tmp/am/TAG.lst
import sys, struct; sys.path.insert(0, '/home/claude/tools')
from walker import *
from walker import _MAPNAME
import os
_ONLY = os.environ.get('MAPS', '').split(',') if os.environ.get('MAPS') else None
rom, st, mode, tag = sys.argv[1:5]
r = open(rom, 'rb').read()
def u32(a): return struct.unpack_from('<I', r, a - 0x08000000)[0]
base = u32(0x080824E0)          # gWildMonHeaders（151匹揃う版は うつした 表）
maps = []
i = 0
while r[base - 0x08000000 + 20 * i] != 0xFF:
    k = (r[base - 0x08000000 + 20 * i], r[base - 0x08000000 + 20 * i + 1])
    if k not in maps: maps.append(k)
    i += 1

def runscript(g, data):
    buf = g.R['strbuf'] + 0x200
    for i, b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a, v in ((0x03000EB1, b'\x01'), (0x03000EB0, b'\x00'), (0x03000EB8, struct.pack('<I', buf)), (0x03000EA8, b'\x00')):
        for i, b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')

OVERWORLD = 0x08055E51
out = []
for (gr, nm) in maps:
    name = _MAPNAME.get((gr, nm), f'{gr}_{nm}')
    if _ONLY and name not in _ONLY: continue
    # マップごとに よみなおす（イベントや バトルが つぎの マップに のこらない）
    g = Game('jp', st, rom=rom); g.run(10)
    g.setflag(0x829); g.setvar(0x4020, 250)
    sb2 = g.u32(0x03004FAC)
    for i, b in enumerate([0x5B, 0x64, 0x5C, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]): g.cmd(f'poke {sb2+i:08X} {b:02X}')
    # ポッポ・コイキング・ズバットを つかまえた ことに（こい色の 表示を みる）
    runscript(g, b''.join(bytes([0x79]) + struct.pack('<HBHIIB', sp, 5, 0, 0, 0, 0) for sp in (16, 129, 41)) + b'\x02'); g.run(80)
    g.teleport(name, 5, 5); g.run(150)
    for k in range(12):
        if not g.script_running(): break
        g.tap('B'); g.run(30)
    note = '' if g.cb2() == OVERWORLD else 'NOT_OVERWORLD'
    pre = f'/tmp/am/{tag}_{gr}_{nm}_'
    if mode == 'field':
        g.tap('S'); g.run(40)
        for k in range(4): g.cmd('tap D 1'); g.run(6)
        g.tap('A'); g.run(40); g.shot(pre + 'a.png')
        for k in range(12): g.cmd('tap D 1'); g.run(5)
        g.run(10); g.shot(pre + 'b.png')
        g.tap('B'); g.run(40); g.shot(pre + 'c.png')
    else:
        g.tap('S'); g.run(40); g.tap('A'); g.run(200)
        for k in range(14): g.cmd('tap D 1'); g.run(4)
        g.tap('A'); g.run(30); g.shot(pre + 'a.png')
        for k in range(12): g.cmd('tap D 1'); g.run(5)
        g.run(10); g.shot(pre + 'b.png')
        g.tap('B'); g.run(30); g.shot(pre + 'c.png')
    g.close()
    out.append((name, pre + 'a.png', pre + 'b.png', pre + 'c.png', note)); print(name, note, flush=True)
open(f'/tmp/am/{tag}.lst', 'w').write('\n'.join('\t'.join(o) for o in out))
