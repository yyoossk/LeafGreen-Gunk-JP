import sys; sys.path.insert(0,'/home/claude/lgtools')
from cap_base import *
R=sys.argv[1] if len(sys.argv)>1 else '/home/claude/work/port.gba'
g=base(R); bag(g,'balls',[(4,10),(3,5)]); setvar(g,0x4020,0)
teleport(g,'ROUTE1',11,30); g.run(30)
w,h,cells,beh=g.grid()
gr=[(x-7,y-7) for y in range(h) for x in range(w) if beh(cells[y*w+x]&0x3FF)==2 and 0<=x-7 and 0<=y-7]
px,py=g.pos()[:2]
gr.sort(key=lambda p:abs(p[0]-px)+abs(p[1]-py)); print(gr[:5])
g.goto(*gr[0]); print(g.pos())
for k in range(200):
    g.hold('L' if k%2 else 'R',16); g.run(2)
    if g.in_battle(): break
for i in range(400):
    if g.in_battle() and g.u32(g.R['bcf'])==g.R['act']: break
    g.tap('B'); g.run(4)
g.run(30); g.shot('/tmp/cap/wild.png'); print('battle',g.in_battle()); g.close()
