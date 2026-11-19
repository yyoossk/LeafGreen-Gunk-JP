import sys; sys.path.insert(0, "/home/claude/tools")
from playtest import *
import walker
def go(g, rec):
    g.handle(rec)
    print(g.k,'objs',g.objects(),flush=True)
    g.explore(rec)
    print(g.k,'after explore',g.pos(),g.party(),flush=True)
    g.go(['PALLET_TOWN'], rec); g.handle(rec)
    print(g.k,'end',g.pos(),g.party(),flush=True)
run_segment('s02_lab', 's01_oak', go)
