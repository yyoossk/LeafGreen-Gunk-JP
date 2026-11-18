import sys; sys.path.insert(0,'/home/claude/tools')
from t151 import *
g=Game('jp','/tmp/walkst/s13_pewter_jp.ss',rom=ROM)
g.run(30)
print('start',g.pos(),count(g))
print('tp',teleport(g,'CELADON_CITY_CONDOMINIUMS_ROOF_ROOM',7,5))
setcount(g,1); sh=[]
for k in range(4):
    r=talk(g,7,3,sh,f'eevee{k}',first='B',then='B')
    print(k,r,'count',count(g),'var',getvar(g,0x40A0),'flag263',getflag(g,0x263),'ballflag57',getflag(g,0x57))
g.save('/tmp/t151/eevee.ss'); g.close()
