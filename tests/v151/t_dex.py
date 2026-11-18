import sys; sys.path.insert(0,'/home/claude/tools')
from t151 import *
g=Game('jp','/tmp/walkst/s13_pewter_jp.ss',rom=ROM); g.run(30)
sb=sb1(g); sb2=g.u32(0x03004FAC)
i=68; byte=i//8; bit=1<<(i%8)
for a in (sb2+0x28,sb2+0x5C,sb+0x5F8,sb+0x3A18):
    v=g.u8(a+byte); poke(g,a+byte,bytes([v|bit]))
g.tap('S'); g.run(30); snap(g,'dx_0'); g.tap('A'); g.run(90); snap(g,'dx_1'); g.tap('A'); g.run(90); snap(g,'dx_2')
g.save('/tmp/t151/dex.ss'); g.close()
