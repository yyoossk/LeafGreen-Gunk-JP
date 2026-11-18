import sys; sys.path.insert(0,'/home/claude/tools')
from t151 import *
g=Game('jp','/tmp/t151/dex.ss',rom=ROM)
for k in range(68): g.tap('D')
g.run(30); snap(g,'dy_0'); g.tap('A'); g.run(120); snap(g,'dy_1'); g.tap('R'); g.run(60); snap(g,'dy_2'); g.tap('A'); g.run(120); snap(g,'dy_3'); g.run(120); snap(g,'dy_4')
g.close()
