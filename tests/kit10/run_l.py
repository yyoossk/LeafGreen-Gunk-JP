import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp',sys.argv[2],rom=sys.argv[1]); g.run(30); g.setflag(0x82F)
g.teleport('ROUTE1',10,30); g.setvar(0x4020,250); g.run(60)
for btn,mod in (('l','B'),('r','B')):
    opened=None
    for f in range(40):
        g.cmd(f'hold U{mod}{btn} 1'); g.cmd(f'hold U{mod} 1')
        if g.u32(0x030030F4)!=0 and False: pass
    g.run(80); g.shot(f'/tmp/t10/run_{btn}.png'); g.tap('B'); g.run(120); print(btn,'pos after',g.pos())
# bike
g.cmd('poke 0 0')
g.close()
