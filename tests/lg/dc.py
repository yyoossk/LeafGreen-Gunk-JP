import sys; sys.path.insert(0,'/home/claude/lgtools'); sys.path.insert(0,'/home/claude/tools')
from cap_base import *
g=base(sys.argv[1], party=((3,20,(76,0,0,0)),(1,30,(33,0,0,0))))
poke(g, sb1(g)+0x290, struct.pack('<I',99999^g.u32(g.u32(0x03004FAC)+0xF20)))
teleport(g,'ROUTE5_POKEMON_DAY_CARE',4,5); g.run(30); g.face('U'); g.run(10)
g.tap('A'); g.run(80); g.shot('/tmp/t2/d0.png')
for i in range(3): g.tap('A'); g.run(60)
g.shot('/tmp/t2/d1.png'); g.tap('D'); g.run(10); g.tap('A'); g.run(90); g.shot('/tmp/t2/d2.png'); g.tap('A'); g.run(40); g.tap('A'); g.run(120); g.shot('/tmp/t2/d3.png')
for i in range(8): g.tap('A'); g.run(50)
print('idle',g.idle())
# add exp by walking a lot: poke steps instead -> walk 300 steps in place
for i in range(80): g.hold('L',16); g.hold('R',16)
g.run(60); g.face('U'); g.run(30); g.tap('A')
for i in range(12):
    g.run(15); g.shot(f'/tmp/t2/e{i}.png')
g.close()
