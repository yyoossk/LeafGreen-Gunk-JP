import sys; sys.path.insert(0, "/home/claude/tools")
from playtest import *
import walker
def go(g, rec):
    g.handle(rec)
    g.go(['PALLET_TOWN_PLAYERS_HOUSE_1F'], rec); g.explore(rec)
    g.go(['PALLET_TOWN'], rec); g.explore(rec)
    # north exit -> Oak stops the player and takes him to the lab
    for i in range(3):
        try: g.edge('U', rec)
        except Exception as e: print('edge', e)
        g.handle(rec)
        if g.pos()[2:]==tuple(walker._MAPS['PALLET_TOWN_PROFESSOR_OAKS_LAB']) if isinstance(walker._MAPS['PALLET_TOWN_PROFESSOR_OAKS_LAB'],tuple) else False: break
    print(g.k, 'after oak', g.pos(), flush=True)
run_segment('s01_oak', 's00_room', go)
