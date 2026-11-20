import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp',None,rom='/home/claude/roms/Pocket Monsters - LeafGreen (Japan) (Rev 1).gba')
for c in ['run 900','tap A 3','run 200','tap A 96','tap A 72','tap A 48','run 300','tap A 6','tap B 6','run 60']: g.cmd(c)
g.run(30); print(g.pos()); g.shot('/tmp/t7/a.png'); g.save('/tmp/t7/van.ss'); g.close()
