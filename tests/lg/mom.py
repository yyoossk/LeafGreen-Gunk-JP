import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom=sys.argv[1]
g=Game('jp','/tmp/t2/after_reload.ss',rom=rom); g.run(10)
print('bdash',g.getflag(0x82F),'pewter var',g.getvar(0x406C))
print(g.teleport('PALLET_TOWN_PLAYERS_HOUSE_1F',8,5))
g.face('U') if hasattr(g,'face') else None
g.run(10)
g.tap('A'); 
for i in range(14):
    g.run(40); g.shot(f'/tmp/t2/mom{i:02d}.png'); g.tap('A')
g.run(120)
print('bdash',g.getflag(0x82F),'hide aide',g.getflag(0x92))
# talk again -> normal
g.tap('A'); g.run(60); g.shot('/tmp/t2/mom_again.png')
for i in range(6): g.tap('A'); g.run(30)
g.close()
