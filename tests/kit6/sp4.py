import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom=sys.argv[1]; tag=sys.argv[2]
g=Game('jp',sys.argv[3] if len(sys.argv)>3 else '/tmp/t4/fresh_new.ss',rom=rom); g.run(10); g.setflag(0x82F)
g.teleport('ROUTE1',16,10); g.run(60); g.hold('D',2); g.run(20)
tr=[]
for k in range(6): g.hold('DB',6); tr.append(g.pos()[1])
print(tag,'y every 6f',tr)
g.close()
