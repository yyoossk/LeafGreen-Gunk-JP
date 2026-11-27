# kit 23：でるポケモンの ボールの アイコン・いろ分け・スクロールの やじるし（リーフグリーン）
# python3 -I bl_lg.py ROM STATE TAG MAP field|dex 0|1     （0/1 ＝ せってい「みてない ポケモン」かくす／みせる）
# レアコイル・ゴルバット・ズバットを つかまえた ことに する（コイル・ズバットは 見ただけ には しない）。モードごとに あたらしい ステート。
import sys, struct; sys.path.insert(0, '/home/claude/tools')
from walker import *
rom, st, tag, mp, mode, show = sys.argv[1:7]
OUT = '/tmp/b23/'
g = Game('jp', st, rom=rom); g.run(10)
g.setflag(0x829); g.setvar(0x4020, 250)
if show == '1': g.setflag(0x4AC)
buf = g.R['strbuf'] + 0x200
data = b''.join(bytes([0x79]) + struct.pack('<HBHIIB', sp, 5, 0, 0, 0, 0) for sp in (82, 42)) + b'\x02'
for i, b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
for a, v in ((0x03000EB1, b'\x01'), (0x03000EB0, b'\x00'), (0x03000EB8, struct.pack('<I', buf)), (0x03000EA8, b'\x00')):
    for i, b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
g.run(80)
g.teleport(mp, 10, 10); g.run(200)
def downs(n):
    for i in range(n): g.cmd('tap D 1'); g.run(6)
def shot(n): g.shot(f'{OUT}{tag}_{n}.png')
if mode == 'field':
    g.tap('S'); g.run(40); downs(4); g.tap('A'); g.run(60); shot('0')
    downs(10); g.run(20); shot('1')
    g.tap('B'); g.run(60); shot('2')
else:
    g.tap('S'); g.run(40); g.tap('A'); g.run(250); downs(14); g.tap('A'); g.run(40); shot('0')
    downs(10); g.run(20); shot('1')
    g.tap('B'); g.run(60); shot('2')
g.close()
