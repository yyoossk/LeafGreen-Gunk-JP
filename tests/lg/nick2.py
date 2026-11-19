import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp','/tmp/walkst/s04_parcel_jp.ss',rom=sys.argv[1]); g.run(20)
g.tap('S'); g.run(30); g.tap('D'); g.run(10); g.tap('A'); g.run(90); g.tap('A'); g.run(40); g.shot('/tmp/t2/k0.png')
# find なまえ: walk down the list
for i in range(8):
    g.tap('D'); g.run(8)
    g.shot(f'/tmp/t2/k1_{i}.png')
g.close()
