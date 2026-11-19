import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp','/tmp/t4/ng.ss',rom='/home/claude/work/port.gba'); g.run(10)
g.goto(11,2); g.hold('L',20); g.run(10); print(g.pos()); g.hold('L',20)
log=[]
for i in range(40):
    g.run(8); log.append(g.pos()[:2]+(g.pos()[3],g.script_running()))
    if i%4==0: g.shot('/tmp/t4/d%02d.png'%i)
print(log)
for i in range(40): g.tap('A'); g.run(10)
print('end',g.pos(),g.script_running()); g.shot('/tmp/t4/end.png'); g.save('/tmp/t4/after.ss')
p0=g.pos(); g.hold('LB',24); g.run(4); print('run 24f L+B',p0,g.pos())
g.close()
