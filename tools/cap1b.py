import sys; sys.path.insert(0,'/home/claude/lgtools')
from cap_base import *
R='/home/claude/work/port.gba'
def S(g,n): g.shot(f'/tmp/cap/{n}.png')
def setup():
    g=base(R)
    bag(g,'tm',[(339,1),(340,1),(341,1),(342,1)])
    bag(g,'key',[(52,1),(53,1),(366,1),(364,1),(357,1),(358,1)])
    bag(g,'med',[(13,10),(22,3)])
    bag(g,'held',[(200,1)])
    bag(g,'balls',[(4,10),(3,5)])
    return g
# A follower
g=setup(); teleport(g,'PALLET_TOWN',12,8); g.run(30)
g.hold('D',48); g.run(30); S(g,'fol1')
g.face('U'); g.run(10); g.tap('A'); g.run(70); S(g,'fol2'); g.close()
# B cut
g=setup(); teleport(g,'VERMILION_CITY',19,26); g.run(30); g.hold('U',16); g.run(20); g.face('U'); g.run(10)
g.tap('A'); g.run(80); S(g,'cut1'); g.tap('A'); g.run(90); S(g,'cut2'); g.tap('A'); g.run(90); S(g,'cut3'); g.run(60); S(g,'cut4'); g.close()
# C party menu, G summary
g=setup(); teleport(g,'PALLET_TOWN',12,10); g.run(30)
g.tap('S'); g.run(30); g.tap('D'); g.run(10); g.tap('A'); g.run(80); g.tap('A'); g.run(40); S(g,'party')
g.tap('A'); g.run(120); S(g,'sum0'); g.tap('R'); g.run(60); S(g,'sum1'); g.tap('A'); g.run(40); S(g,'sum2'); g.tap('A'); g.run(40); S(g,'sum3')
g.close()
# F wild battle
g=setup(); setvar(g,0x4020,0); teleport(g,'ROUTE1',11,30); g.run(30); g.hold('R',32); g.run(10)
for k in range(120):
    g.hold('D' if k%2 else 'U',16); g.run(2)
    if g.in_battle(): break
for i in range(300):
    if g.in_battle() and g.u32(g.R['bcf'])==g.R['act']: break
    g.tap('B'); g.run(4)
g.run(30); S(g,'wild'); g.close()
