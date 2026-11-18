import sys; sys.path.insert(0,'/home/claude/tools')
from t151 import *
import collections
g=Game('jp','/tmp/walkst/s13_pewter_jp.ss',rom=ROM); g.run(30)
setvar(g,0x4020,0)
print(teleport(g,'ROUTE24',4,27))
sb=sb1(g)
for b in range(0xA0,0x100): poke(g,sb+0xEE0+b,b'\xff')
# find grass near: walk left/right
seen=collections.Counter(); n=0
while n<40 and g.frames<200000:
    for d in 'UD':
        g.hold(d,16); g.run(2)
        if g.in_battle() or not g.idle():
            for i in range(200):
                if g.in_battle() and g.u32(g.R['bcf'])==g.R['act']: break
                g.tap('B')
            sp=g.u16(g.R['bmons']+0x58); lv=g.u8(g.R['bmons']+0x58+0x2A); seen[sp]+=1; n+=1
            if n==1: snap(g,'wild1')
            for i in range(120):
                if g.in_overworld() and g.idle(): break
                if g.in_battle() and g.u32(g.R['bcf'])==g.R['act']:
                    g.tap('D'); g.tap('R'); g.tap('A')
                else: g.tap('B')
            poke(g,0x02024284-0x2024284+0x020241E4+86,b'\x50')  # keep hp
print(n, sorted(seen.items()))
