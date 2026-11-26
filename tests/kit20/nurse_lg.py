# kit 20：ポケモンセンターの かいふく（リーフグリーン）
# python3 -I nurse_lg.py ROM STATE TAG heal 0|1     A れんだで かいふく（1＝せってい「かいふく アニメ」みない）
# python3 -I nurse_lg.py ROM STATE TAG no          「いいえ」の ときは むきが かわらない
# python3 -I nurse_lg.py ROM STATE TAG option      せっていの 7行・「かいふく アニメ」を きりかえて とじると フラグが かわる
import sys, struct; sys.path.insert(0, '/home/claude/tools')
from walker import *
rom, st, tag, mode = sys.argv[1:5]
OUT = '/tmp/nu20/'
g = Game('jp', st, rom=rom); g.run(10)
P = g.R['party']
FLAG = 0x4AB
def getflag(f):
    sb1 = g.u32(0x03004FA8); return (g.u8(sb1 + 0xEE0 + f // 8) >> (f % 8)) & 1
def facing():
    oid = g.u8(g.R['avatar'] + 5); return g.u8(g.R['objs'] + oid * 0x24 + 0x18) & 0xF
def shot(n): g.shot(f'{OUT}{tag}_{n}.png')
def to_nurse():
    # したから あるいて くる（つれあるきが うしろに つく）
    g.teleport('VIRIDIAN_CITY_POKEMON_CENTER_1F', 7, 8); g.run(60)
    for i in range(40):
        if g.pos()[1] <= 4: break
        g.cmd('hold U 4'); g.run(4)
    g.run(40); g.face('U'); g.run(10)
    print(tag, 'pos', g.pos())

if mode == 'heal':
    if sys.argv[5] == '1': g.setflag(FLAG)
    g.cmd(f'poke {P+0x56:08X} 01'); g.cmd(f'poke {P+0x57:08X} 00')
    to_nurse()
    frames = 0; done = None; talks = 0; was = False; v0 = g.u32(0x03003090 + 0x24)
    for i in range(200):
        g.tap('A'); g.run(6); frames += 7
        if g.u16(P + 0x56) > 1 and done is None: done = g.u32(0x03003090 + 0x24) - v0
        run = g.script_running()
        if run and not was: talks += 1
        was = run
        if done and not run and g.idle():
            print(tag, 'talks_until_heal_end', talks, 'guard_left', g.u32(0x0203FFAC) - g.u32(0x03003090 + 0x24))
            t0 = g.u32(0x03003090 + 0x24)   # gMain.vblankCounter2
            for j in range(60):          # かいふくの あとも 4フレームごとに A を おしつづける（やく 3びょう）
                g.cmd('tap A 1'); g.run(4)
                run = g.script_running()
                if run and not was: talks += 1; print(tag, 'talk_after_heal_frames', g.u32(0x03003090 + 0x24) - t0, 'guard_left', g.u32(0x0203FFAC) - g.u32(0x03003090 + 0x24))
                was = run
                if j in (0, 20, 59): shot(f'm{j:02d}')
                if run: break
            break
    print(tag, 'heal_frames', done, 'talks', talks, 'facing', facing(), 'idle', g.idle(), 'hp', g.u16(P + 0x56))
    g.run(150); g.tap('A'); g.run(60); shot('later')
    print(tag, 'later_talk_follower', g.script_running())
elif mode == 'no':
    to_nurse()
    g.tap('A'); g.run(60); g.tap('A'); g.run(30); g.cmd('tap D 1'); g.run(10); g.tap('A'); g.run(60); shot('no'); g.tap('A'); g.run(60)
    for i in range(10): g.tap('B'); g.run(10)
    print(tag, 'facing_after_no', facing(), 'idle', g.idle())
elif mode == 'option':
    g.setflag(0x829)
    # スタートメニュー：ずかん ポケモン バッグ パソコン でるポケモン なまえ レポート せってい
    g.tap('S'); g.run(40); shot('menu')
    for k in range(7): g.cmd('tap D 1'); g.run(6)
    g.tap('A'); g.run(90); shot('op0')
    for i in range(6): g.cmd('tap D 1'); g.run(8)
    g.cmd('tap R 1'); g.run(10); shot('op1')
    g.tap('B'); g.run(120); shot('cl1'); print(tag, 'flag_after_toggle', getflag(FLAG))
    g.tap('A'); g.run(90); shot('op2')            # とじると スタートメニューの「せってい」に もどる
    for i in range(6): g.cmd('tap D 1'); g.run(8)
    g.cmd('tap R 1'); g.run(10); shot('op3')
    g.tap('A'); g.run(120); shot('cl2'); print(tag, 'flag_after_toggle2', getflag(FLAG))
g.close()
