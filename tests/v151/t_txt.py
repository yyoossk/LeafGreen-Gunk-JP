import sys; sys.path.insert(0,'/home/claude/tools')
from t151 import *
g=Game('jp','/tmp/walkst/s13_pewter_jp.ss',rom=ROM); g.run(30); sh=[]
teleport(g,'ROUTE24',6,9); talk(g,6,8,sh,'tc',first='A',then='B',n=14)
teleport(g,'VERMILION_CITY',17,9); setflag(g,0x822,False); talk(g,17,8,sh,'ts0',n=8)
setflag(g,0x822,True); talk(g,17,8,sh,'ts1',first='A',then='B',n=10)
print(count(g)); g.close()
