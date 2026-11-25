import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom=sys.argv[1]; st=sys.argv[2]; mp=sys.argv[3]; x,y=int(sys.argv[4]),int(sys.argv[5]); seq=sys.argv[6]
g=Game('jp',st,rom=rom); g.run(10); g.setflag(0x82F); g.setvar(0x4020,250)
g.teleport(mp,x,y); g.run(300)
for part in seq.split(','):
    k,n=part.split(':'); g.cmd(f'hold {k} {n}')
    ob=g.objects(); print(k,n,[(o[1],o[2],o[3]) for o in ob if o[3] in (0,152)] , g.pos())
g.shot(f'/tmp/fol/{mp}.png'); g.peek(0,1); g.close()
