import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
from PIL import Image
rom,st,tag=sys.argv[1],sys.argv[2],sys.argv[3]
for name,(m,x,y) in {'cinnabar':('CINNABAR_ISLAND',20,7)}.items():
    g=Game('jp',st,rom=rom); g.run(10); g.setvar(0x4020,250); g.setflag(0x1A8)
    g.teleport(m,x,y); g.run(120)
    for i in range(4): g.hold('U',20); g.run(10)
    g.run(200); p=g.pos(); g.shot(f'/tmp/t15/{tag}_{name}.png')
    for i in range(3): g.hold('D',20); g.run(10)
    g.run(200); q=g.pos(); g.shot(f'/tmp/t15/{tag}_{name}_out.png')
    print(tag,name,'in',p,'out',q)
    g.close()
