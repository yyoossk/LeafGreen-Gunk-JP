import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
for keys in ('R','BR'):
    g=Game('jp','/tmp/t2/after_reload.ss',rom=sys.argv[1]); g.run(10); g.setflag(0x82F)
    g.teleport('PALLET_TOWN',6,8); g.run(60)
    x0=g.pos()[0]; g.hold(keys,64); g.run(20); print(keys,'moved',g.pos()[0]-x0); g.shot(f'/tmp/t2/bd_{keys}.png'); g.close()
