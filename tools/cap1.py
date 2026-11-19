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
g.tap('A'); g.run(80); S(g,'cut1'); g.tap('A'); g.run(90); S(g,'cut2'); g.close()
# C party menu, G summary
g=setup(); teleport(g,'PALLET_TOWN',12,10); g.run(30)
g.tap('S'); g.run(30); g.tap('D'); g.run(10); g.tap('A'); g.run(80); g.tap('A'); g.run(40); S(g,'party')
g.tap('A'); g.run(120); S(g,'sum0'); g.tap('R'); g.run(60); S(g,'sum1'); g.tap('A'); g.run(40); S(g,'sum2'); g.tap('A'); g.run(40); S(g,'sum3')
g.close()
# D menu PC
g=setup(); teleport(g,'PALLET_TOWN',12,10); g.run(30)
g.tap('S'); g.run(30); g.tap('D',3); g.run(10); S(g,'mpc0'); g.tap('A'); g.run(90); g.tap('A'); g.run(60); S(g,'mpc1'); g.close()
# E bag
g=setup(); teleport(g,'PALLET_TOWN',12,10); g.run(30)
g.tap('S'); g.run(30); g.tap('D',2); g.run(10); g.tap('A'); g.run(90); S(g,'bag0')
for i in range(6): g.tap('R'); g.run(30); S(g,f'bag{i+1}')
g.close()
# F wild battle
g=setup(); teleport(g,'ROUTE1',11,30); g.run(30)
for k in range(60):
    g.hold('L' if k%2 else 'R',16); g.run(2)
    if g.in_battle(): break
for i in range(300):
    if g.in_battle() and g.u32(g.R['bcf'])==g.R['act']: break
    g.tap('B'); g.run(4)
g.run(30); S(g,'wild'); g.close()
# H TM shop (postgame)
g=setup(); setflag(g,0x82C); poke(g,sb1(g)+0x290,struct.pack('<I',131892^g.u32(g.u32(0x03004FAC)+0xF20)))
teleport(g,'CELADON_CITY_DEPARTMENT_STORE_2F',2,6); g.run(30); g.face('L'); g.run(10)
g.tap('A'); g.run(60); g.tap('A'); g.run(60); g.tap('A'); g.run(60); S(g,'tm0'); g.tap('A'); g.run(40); S(g,'tm1'); g.close()
