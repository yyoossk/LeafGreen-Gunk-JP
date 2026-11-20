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
tag=sys.argv[3]
S=[]
def sh(n): g.shot(f'/tmp/t10/h_{tag}_{n}.png'); S.append(n)
g.tap('A'); g.run(40); sh('moves')
g.tap('l'); g.run(60); sh('moves_L')
g.tap('B'); g.run(40); g.tap('r'); g.run(60); sh('moves_R')
g.tap('B'); g.run(40)
# pick first move, then press L/R during messages
g.tap('A'); g.run(10); g.tap('A'); g.run(30); g.tap('r'); g.run(30); sh('msg_R'); g.tap('l'); g.run(30); sh('msg_L')
for k in range(30): g.tap('B'); g.run(10)
g.close()
from PIL import Image
W=Image.new('RGB',(240*len(S),160))
for i,n in enumerate(S): W.paste(Image.open(f'/tmp/t10/h_{tag}_{n}.png').convert('RGB'),(i*240,0))
W.save(f'/tmp/t10/h_{tag}.png')
