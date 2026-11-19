import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom=sys.argv[1]
g=Game('jp','/tmp/t2/after_reload.ss',rom=rom); g.run(10)
g.tap('S'); g.run(30); g.shot('/tmp/t2/m0.png')
g.tap('D',3); g.run(10); g.shot('/tmp/t2/m1.png')
g.tap('A'); g.run(90); g.shot('/tmp/t2/m2.png')
g.tap('A'); g.run(60); g.shot('/tmp/t2/m3.png')
g.tap('A'); g.run(60); g.shot('/tmp/t2/m4.png')   # storage menu
g.tap('A'); g.run(220); g.shot('/tmp/t2/m5.png')  # withdraw
g.tap('B'); g.run(150); g.tap('B'); g.run(150); g.shot('/tmp/t2/m6.png')
for i in range(4): g.tap('B'); g.run(60)
g.shot('/tmp/t2/m7.png'); print('idle',g.idle(),g.pos())
# save then continue: quest log should not play
g.hold('L',40); g.run(30)
g.tap('S'); g.run(30); g.tap('D',5); g.shot('/tmp/t2/m8.png'); g.tap('A'); g.run(60); g.tap('A'); g.run(400); g.tap('A'); g.run(60)
g.shot('/tmp/t2/m9.png')
g.cmd('reset'); g.run(900); g.tap('A'); g.run(200); g.shot('/tmp/t2/m10.png'); g.tap('A'); g.run(300)
g.shot('/tmp/t2/m11.png'); g.run(200); g.shot('/tmp/t2/m12.png'); print('after continue',g.idle(),g.pos())
g.close()
