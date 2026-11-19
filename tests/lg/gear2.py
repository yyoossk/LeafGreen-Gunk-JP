import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
for gear in (0,1):
    g=Game('jp','/tmp/walkst/s21_postgame_jp.ss',rom=sys.argv[1]); g.run(10)
    g.teleport('PALLET_TOWN',12,8); g.run(30)
    sb1=g.u32(0x03004FA8)
    g.cmd(f'poke {sb1+0x296:08X} 68'); g.cmd(f'poke {sb1+0x297:08X} 01')
    g.tap('s'); g.run(40)
    if gear: g.tap('B'); g.run(10)
    p0=g.pos(); g.hold('U',48); g.run(30); p1=g.pos()
    print('gear',g.getflag(0xE3),p0,p1, 'tiles',p0[1]-p1[1]); g.shot(f'/tmp/t2/gr{gear}.png')
    g.close()
