import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom=sys.argv[1]; tag=sys.argv[2]
g=Game('jp','/tmp/t4/fresh_new.ss',rom=rom); g.run(10)
g.teleport('VIRIDIAN_CITY',14,5); g.run(80)
ev=g.events(); print([e for e in ev if 'obj' in str(e)][:0])
g.hold('R',40); g.run(30); g.tap('R'); g.run(20); print(g.pos(),g.facing())
g.tap('A'); g.run(90); g.shot(f'/tmp/t5/{tag}_pk0.png'); g.tap('A'); g.run(60); g.shot(f'/tmp/t5/{tag}_pk1.png'); g.tap('A'); g.run(60)
print(tag,'flag 0x1CD',g.getflag(0x1cd))
g.close()
