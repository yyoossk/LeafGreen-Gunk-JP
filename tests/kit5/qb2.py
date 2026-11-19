import sys; sys.path.insert(0,'/home/claude/lgtools')
from cap_base import *
R=sys.argv[1]; tag=sys.argv[2]
g=base(R); bag(g,'balls',[(4,10),(3,5)]); setvar(g,0x4020,0)
teleport(g,'ROUTE1',11,30); g.run(30)
w,h,cells,beh=g.grid()
gr=[(x-7,y-7) for y in range(h) for x in range(w) if beh(cells[y*w+x]&0x3FF)==2 and 0<=x-7 and 0<=y-7]
px,py=g.pos()[:2]; gr.sort(key=lambda p:abs(p[0]-px)+abs(p[1]-py)); g.goto(*gr[0])
for k in range(200):
    g.hold('L' if k%2 else 'R',16); g.run(2)
    if g.in_battle(): break
for i in range(400):
    if g.in_battle() and g.u32(g.R['bcf'])==g.R['act']: break
    g.tap('B'); g.run(4)
g.run(30); g.shot(f'/tmp/t5/{tag}_q0.png')
if len(sys.argv)>3 and sys.argv[3]=='B':
    g.tap('B'); g.run(30); g.tap('B'); g.run(30)
sb=sb1(g); key=g.u16(g.u32(0x03004FAC)+0xF20); print('balls before',[g.u16(sb+0x430+4*i+2)^key for i in range(2)])
for fr in range(0,600,100):
    g.run(1) if fr==0 else None
    if fr==0: g.tap('l')
    g.run(100); g.shot(f'/tmp/t5/{tag}_r%d.png'%(fr//100))
print('balls after',[g.u16(sb+0x430+4*i+2)^key for i in range(2)],'inbattle',g.in_battle())
g.close()
