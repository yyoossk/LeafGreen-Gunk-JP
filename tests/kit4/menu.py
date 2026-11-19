import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp','/tmp/t4/fresh_new.ss',rom='/home/claude/work/port.gba'); g.run(20)
g.tap('START'); g.run(40); g.shot('/tmp/t4/menu7.png'); g.tap('B'); g.run(30); g.shot('/tmp/t4/menu_closed.png'); g.close()
