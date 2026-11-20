import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp',sys.argv[2],rom=sys.argv[1]); g.run(30)
pos=lambda: (g.u16(g.u32(0x03004FA8)), g.u16(g.u32(0x03004FA8)+2))
print('start',pos())
g.tap('l'); g.run(90); g.tap('B'); g.run(120); g.hold('U',40); g.run(20); print('after L',pos())
g.tap('r'); g.run(90); g.tap('B'); g.run(120); g.hold('D',40); g.run(20); print('after R',pos())
# run and press L while moving
g.cmd('hold BU 30'); g.tap('l'); g.run(120); g.shot('/tmp/t2/lr6.png'); g.tap('B'); g.run(120); g.shot('/tmp/t2/lr7.png')
g.close()
