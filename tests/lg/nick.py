import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp','/tmp/t2/after_reload.ss',rom=sys.argv[1]); g.run(20)
g.tap('S'); g.run(20); g.tap('A'); g.run(60); g.tap('A'); g.run(30); g.shot('/tmp/t2/n0.png')
g.tap('D',3); g.run(8); g.shot('/tmp/t2/n1.png')
g.tap('A'); g.run(120); g.shot('/tmp/t2/n2.png')
# type: press A on first char a few times
g.tap('B',6); g.run(20); g.tap('A',2); g.run(10); g.shot('/tmp/t2/n3.png')
g.tap('S'); g.run(10); g.tap('A'); g.run(150); g.shot('/tmp/t2/n4.png')
g.tap('B'); g.run(60); g.tap('B'); g.run(60); g.shot('/tmp/t2/n5.png')
g.close()
