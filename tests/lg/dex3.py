import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp','/tmp/walkst/s21_postgame_jp.ss',rom=sys.argv[1]); g.run(10)
sb2=g.u32(0x03004FAC)
sb1=g.u32(0x03004FA8)
for i in range(52):
    for a in (sb2+0x28+i, sb2+0x5C+i, sb1+0x5F8+i, sb1+0x3A18+i): g.cmd(f'poke {a:08X} FF')
g.tap('S'); g.run(20); g.tap('A'); g.run(120); g.tap('A'); g.run(80); g.tap('A'); g.run(90)
d=g.u32(0x0203AC68)
for k,sp in enumerate((133,64,143,150)):
    g.cmd(f'poke {d+0x5A:08X} {sp&0xff:02X}'); g.cmd(f'poke {d+0x5B:08X} {sp>>8:02X}')
    g.tap('s'); g.run(30); g.shot(f'/tmp/t2/de{k}.png'); g.tap('s'); g.run(20)
g.close()
