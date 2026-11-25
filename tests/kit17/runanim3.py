import sys,struct,hashlib; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom,st,t,key=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
g=Game('jp',st,rom=rom); g.run(10); g.setflag(0x82F); g.setvar(0x4020,250)
g.teleport('VIRIDIAN_CITY',20,20); g.run(120)
g.cmd(f'hold {key} 10')
names={}; s=''
for i in range(36):
    g.cmd(f'hold {key} 1')
    o=g.peek(0x07000000,8*128); best=None
    for k in range(128):
        a0,a1,a2=struct.unpack('<HHH',o[k*8:k*8+6])
        if (a0>>8)&3==2: continue
        y=a0&0xFF; x=a1&0x1FF; shape=a0>>14; size=a1>>14
        if shape==2 and size==2 and 100<=x<=124 and 40<=y<=72:   # 16x32
            best=(a2&0x3FF); break
    if best is None: s+='?'; continue
    h=hashlib.md5(g.peek(0x06010000+best*32,256)).hexdigest()
    s+=names.setdefault(h,chr(65+len(names)))
g.close(); print(t,key,s)
