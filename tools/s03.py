import sys; sys.path.insert(0, "/home/claude/tools")
from playtest import *
import walker
def go(g, rec):
    g.handle(rec)
    g.interact(9, 4, 'starter', rec, key='A')
    for i in range(10):
        g.handle(rec)
        if g.party(): break
        g.tap('A'); g.run(30)
    print(g.k,'party',g.party(),g.pos(),flush=True)
    for i in range(4):
        try: g.go(['PALLET_TOWN'], rec)
        except Exception as e: print('go',e)
        g.handle(rec)
        if g.pos()[2:]==(3,0): break
    print(g.k,'end',g.pos(),g.party(),flush=True)
run_segment('s03_starter', 's02_lab', go)
