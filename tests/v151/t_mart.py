import sys; sys.path.insert(0,'/home/claude/tools')
from t151 import *
g=Game('jp','/tmp/walkst/s13_pewter_jp.ss',rom=ROM); g.run(30)
teleport(g,'CELADON_CITY_DEPARTMENT_STORE_4F',4,13)
g.face('L'); g.tap('A'); g.run(60); g.tap('A'); g.run(60)
for k in range(6): g.tap('D'); g.run(8)
snap(g,'mt_4'); g.close()
