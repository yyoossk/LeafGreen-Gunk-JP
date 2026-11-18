import sys; sys.path.insert(0,'/home/claude/tools')
from t151 import *
g=Game('jp','/tmp/walkst/s13_pewter_jp.ss',rom=ROM); g.run(30)
teleport(g,'CELADON_CITY_GAME_CORNER_PRIZE_ROOM',4,4)
setflag(g,0x243)
sb=sb1(g); sb2=g.u32(0x03004FAC); key=g.u16(sb2+0xF20)
poke(g, sb+0x294, struct.pack('<H',9999^key)); setcount(g,1)
g.face('U'); g.tap('A'); g.run(60); g.tap('A'); g.run(60)
g.tap('D'); g.run(10); g.tap('D'); g.run(10); snap(g,'pq_0'); g.tap('A'); g.run(60); snap(g,'pq_1'); g.tap('A'); g.run(60); snap(g,'pq_2')
for i in range(20):
    if g.idle(): break
    g.tap('B'); g.run(20)
    if i<6: snap(g,f'pq_b{i}')
print('count',count(g),'coins',g.u16(sb1(g)+0x294)^key)
d=g.peek(0x020241E4+100,100); import mkmon
print('slot1 nick bytes', d[8:18].hex())
teleport(g,'CELADON_CITY_DEPARTMENT_STORE_4F',4,13)
g.face('L'); g.tap('A'); g.run(60); snap(g,'mt_0'); g.tap('A'); g.run(60); snap(g,'mt_1'); g.tap('A'); g.run(60); snap(g,'mt_2')
for k in range(6): g.tap('D'); g.run(8)
snap(g,'mt_3'); g.close()
