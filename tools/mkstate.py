import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
import mkmon
rom=sys.argv[1]; out=sys.argv[2]
g=Game('jp',None,rom=rom)
for c in ['run 900','tap A 3','run 200','tap A 96','tap A 72','tap A 48','run 300','tap A 6','tap B 6','run 60']: g.cmd(c)
g.setflag(0x828); g.setflag(0x829)
d=mkmon.mon(1,level=8,moves=(33,45,0,0),pid=0x1001)
for i,b in enumerate(d): g.cmd(f'poke {g.R["party"]+i:08X} {b:02X}')
g.cmd(f'poke {g.R["cnt"]:08X} 01')
g.run(30); g.teleport('PALLET_TOWN_PLAYERS_HOUSE_1F',3,6); g.run(60); g.face('D'); g.run(20); print(g.pos()); g.save(out); g.close()
