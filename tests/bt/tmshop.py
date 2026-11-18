import sys; sys.path.insert(0, "/home/claude/tools")
from story import *
for k,st in (('jp','/tmp/walkst/s20b_e4_jp.ss'),('jp0','/tmp/walkst/s19_saffron_jp.ss')):
    g=Game('jp',st,rom='/home/claude/work/port151.gba'); g.run(10); rec=[]
    tp(g,rec,'CELADON_CITY_DEPARTMENT_STORE_2F',2,6); g.face('L')
    g.tap('A'); g.run(40); g.shot(f'/tmp/bt/tm_{k}0.png')
    for i in range(3): g.tap('A'); g.run(40); g.shot(f'/tmp/bt/tm_{k}{i+1}.png')
    for i in range(5): g.tap('D'); g.run(5)
    g.shot(f'/tmp/bt/tm_{k}5.png'); g.close()
