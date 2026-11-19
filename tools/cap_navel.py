import sys; sys.path.insert(0,'/home/claude/lgtools')
from cap_base import *
g=base('/home/claude/work/port.gba')
bag(g,'key',[(52,1),(53,1),(370,1)])
for f in (0x82C,0x84A,0x840): setflag(g,f)
setvar(g,0x4076,5); setvar(g,0x407E,3)
teleport(g,'VERMILION_CITY',24,32); g.face('D'); g.run(10)
g.tap('A'); g.run(60); g.shot('/tmp/cap/nv0.png'); g.tap('A'); g.run(80); g.shot('/tmp/cap/nv1.png'); g.tap('B'); g.run(80); g.shot('/tmp/cap/nv2.png')
for i in range(3,10):
    g.tap('A'); g.run(70); g.shot(f'/tmp/cap/nv{i}.png')
g.close()
