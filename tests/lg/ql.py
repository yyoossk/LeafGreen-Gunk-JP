import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp','/tmp/t2/after_reload.ss',rom=sys.argv[1]); g.run(30)
# walk a bit to record quest-log scenes, then save
g.tap('START'); g.run(20); g.tap('DOWN',4); g.tap('A'); g.run(60); g.tap('A'); g.run(400)
for i in range(4): g.tap('A'); g.run(60)
g.cmd('reset'); g.run(600)
k=0
for i in range(14):
    g.tap('A'); g.run(60)
    if i>=6: g.shot(f'/tmp/t2/{sys.argv[2]}{k}.png'); k+=1
print('overworld idle', g.idle(), g.pos())
g.close()
