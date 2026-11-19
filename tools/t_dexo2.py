import sys; sys.path.insert(0,'/home/claude/tools')
from t151 import *
g=Game('jp','/tmp/t151/dexo.ss',rom=ROM)
for k in range(42): g.tap('D')
g.run(30); snap(g,'oy_0'); g.tap('A'); g.run(120); snap(g,'oy_1'); g.tap('R'); g.run(60); snap(g,'oy_2'); g.tap('A'); g.run(120); snap(g,'oy_3'); g.run(120); snap(g,'oy_4')
g.close()
