# kit 22：せってい「みてない ポケモン」（かくす／みせる）と、8行の せってい（リーフグリーン）
# python3 -I un_lg.py ROM STATE TAG on|dex|off
#   on ：ハナダのどうくつで でるポケモン（？？？？？）→ せってい 8行を 1行ずつ → みせる に して とじる → フラグ → でるポケモン（なまえ）
#   dex：フラグ ありで ずかんの でるポケモン（なまえ）
#   off：フラグ ありで せってい を ひらくと「みせる」→ かくす に して とじる → フラグ → でるポケモン（？？？？？）
# スタートメニューの カーソルは まえの いちを おぼえるので、モードごとに あたらしい ステートから はじめる
import sys, struct; sys.path.insert(0, '/home/claude/tools')
from walker import *
rom, st, tag, mode = sys.argv[1:5]
OUT = '/tmp/u22/'
g = Game('jp', st, rom=rom); g.run(10)
g.setflag(0x829); g.setvar(0x4020, 250)
FLAG = 0x4AC
if mode in ('dex', 'off'): g.setflag(FLAG)
def shot(n): g.shot(f'{OUT}{tag}_{mode}_{n}.png')
def downs(n, key='D'):
    for i in range(n): g.cmd(f'tap {key} 1'); g.run(6)
g.teleport('CERULEAN_CAVE_1F', 10, 10); g.run(200)
# スタートメニュー（バッジ なし）：0 ずかん 1 ポケモン 2 バッグ 3 パソコン 4 でるポケモン 5 なまえ 6 レポート 7 せってい
if mode == 'on':
    g.tap('S'); g.run(40); downs(4); g.tap('A'); g.run(60); shot('here_hide')
    g.tap('B'); g.run(60)                       # でるポケモン → スタートメニュー（カーソル 4）
    downs(3); g.tap('A'); g.run(90)             # せってい
    for i in range(8):
        shot(f'row{i}'); g.cmd('tap D 1'); g.run(8)
    downs(7); g.cmd('tap R 1'); g.run(10); shot('toggled')
    g.tap('B'); g.run(120); print(tag, mode, 'flag', g.getflag(FLAG))
    downs(3, 'U'); g.tap('A'); g.run(60); shot('here_show')   # スタートメニュー（カーソル 7）→ 4
elif mode == 'dex':
    # ずかんは 1ぴきも 見て いないと ひらかない：ポッポを もらって おく
    buf = g.R['strbuf'] + 0x200
    data = bytes([0x79]) + struct.pack('<HBHIIB', 16, 5, 0, 0, 0, 0) + b'\x02'
    for i, b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a, v in ((0x03000EB1, b'\x01'), (0x03000EB0, b'\x00'), (0x03000EB8, struct.pack('<I', buf)), (0x03000EA8, b'\x00')):
        for i, b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
    g.run(80)
    g.tap('S'); g.run(60); shot('dex_menu'); g.tap('A'); g.run(300); shot('dex_top'); downs(14); g.run(20); shot('dex_sel'); g.tap('A'); g.run(40); shot('dex_show')
elif mode == 'off':
    g.tap('S'); g.run(40); downs(7); g.tap('A'); g.run(90); shot('reopen')
    downs(7); g.cmd('tap L 1'); g.run(10); shot('hide')
    g.tap('B'); g.run(120); print(tag, mode, 'flag', g.getflag(FLAG))
    downs(3, 'U'); g.tap('A'); g.run(60); shot('here_hide2')
g.close()
