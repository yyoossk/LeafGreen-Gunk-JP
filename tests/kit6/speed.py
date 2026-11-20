import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom=sys.argv[1]; tag=sys.argv[2]
g=Game('jp',sys.argv[3] if len(sys.argv)>3 else '/tmp/t4/fresh_new.ss',rom=rom); g.run(10); g.setflag(0x82F)
# indoor (house 1F): face right then run
g.hold('R',2); g.run(20); p0=g.pos(); g.hold('RB',18); g.run(1); print(tag,'indoor RB 18f',p0[:2],'->',g.pos()[:2])
g.teleport('ROUTE1',10,30); g.run(60)
g.hold('U',2); g.run(20); p0=g.pos(); g.hold('UB',36); g.run(1); print(tag,'outdoor UB 36f',p0[:2],'->',g.pos()[:2])
def objs():
    b=g.peek(g.R['objs'],0x24*16); out=[]
    for i in range(16):
        e=b[0x24*i:0x24*i+0x24]
        if e[0]&1:
            cx,cy=struct.unpack('<hh',e[0x10:0x14]); out.append((i,cx-7,cy-7))
    return out
o=objs(); pl=o[0]; fid=min(o[1:],key=lambda q:abs(q[1]-pl[1])+abs(q[2]-pl[2]))[0]
gaps=[]
for k in range(30):
    g.hold('UB',2); o=objs(); f=[q for q in o if q[0]==fid][0]; gaps.append(abs(o[0][1]-f[1])+abs(o[0][2]-f[2]))
print(tag,'flat run gap',gaps)
g.close()
