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
sb=sb1(g)
if sys.argv[3]=='r':
    g.tap('r'); 
    for k in range(30): g.run(10)
    print('after R in battle:',g.in_battle()); g.shot('/tmp/t10/bt_r.png')
else:
    g.tap('l')
    for k in range(60): g.run(10)
    print('after L in battle:',g.in_battle()); g.shot('/tmp/t10/bt_l.png')
g.close()
