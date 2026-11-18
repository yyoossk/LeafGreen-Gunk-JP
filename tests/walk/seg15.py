import sys; sys.path.insert(0, "/home/claude/tools")
from playtest import *
def go(g, rec):
    g.handle(); g.trail = [mapid('PEWTER_CITY'), mapid('PEWTER_CITY_POKEMON_CENTER_1F')]
    g.go(['PEWTER_CITY'], rec)
    g.go(['ROUTE3'], rec); g.explore(rec)
    g.go(['ROUTE4'], rec)
    g.go(['MT_MOON_POKEMON_CENTER_1F' if 'MT_MOON_POKEMON_CENTER_1F' in walker._MAPS else 'ROUTE4_POKEMON_CENTER_1F'], rec)
    g.heal_center(rec); g.explore(rec)
    g.go(['ROUTE4'], rec); g.explore(rec)
    g.go(['MT_MOON_1F'], rec)
    g.dungeon('ROUTE4', rec, exclude=[('MT_MOON_1F', 3)])
    print(g.k, g.pos(), g.party(), flush=True)
import walker
run_segment('s15_mtmoon', 's14_brock', go)
