import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp','/tmp/t2/after_reload.ss',rom=sys.argv[1]); g.run(10)
g.tap('START'); g.run(20); g.tap('DOWN',2); g.tap('A'); g.run(80); g.tap('A'); g.run(60); g.tap('A'); g.run(60)
g.tap('A')
for i in range(8): g.run(25); g.shot(f'/tmp/t2/s{i}.png')
g.tap('A'); g.run(150); g.shot('/tmp/t2/s8.png')
g.tap('B'); g.run(100); g.tap('B'); g.run(150); g.shot('/tmp/t2/s9.png')
g.close()
