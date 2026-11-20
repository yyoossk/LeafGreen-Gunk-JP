import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom,st=sys.argv[1],sys.argv[2]
g=Game('jp',st,rom=rom); g.run(10); g.setflag(0x82F); g.setvar(0x4020,250)
g.teleport('ROUTE1',16,14); g.run(80)
g.hold('D',40); g.run(30)
def objs():
    b=g.peek(g.R['objs'],0x24*16); out=[]
    for i in range(16):
        e=b[0x24*i:0x24*i+0x24]
        if e[0]&1:
            cx,cy,px,py=struct.unpack('<hhhh',e[0x10:0x18]); out.append((i,cx-7,cy-7))
    return out
res=[]
for i in range(80):
    g.hold('DB',2)
    o=objs(); res.append(o)
    if i in (10,20,30,40): g.shot(st+'_%d.png'%i)
fid=min([o for o in res[0][1:]],key=lambda o:abs(o[1]-res[0][0][1])+abs(o[2]-res[0][0][2]))[0]; print('fid',fid,res[0])
p=[r[0][2] for r in res]; f=[[o[2] for o in r if o[0]==fid][0] for r in res]
print('player y',p[::3]); print('follow y',f[::3])
print('gap',[a-b for a,b in zip(p,f) if b is not None][::3])
g.close()
