import sys; sys.path.insert(0, "/home/claude/tools")
from story import *
def go(g, rec):
    g.handle(); g.trail = []
    power_up(g); print(g.party(), flush=True)
    step(g, rec, 'captain', lambda: (tp(g, rec, 'SSANNE_CAPTAINS_OFFICE', 4, 5), talk(g, rec, 5, 4, 'captain')))
    step(g, rec, 'leave', lambda: (tp(g, rec, 'SSANNE_EXTERIOR', 32, 7), walk(g, rec, 32, 6), g.go(['VERMILION_CITY'], rec), g.handle(rec)))
    step(g, rec, 'fanclub', lambda: (tp(g, rec, 'VERMILION_CITY', 12, 18), g.go(['VERMILION_CITY_POKEMON_FAN_CLUB'], rec), talk(g, rec, 5, 4, 'chairman')))
    step(g, rec, 'bike', lambda: (tp(g, rec, 'CERULEAN_CITY', 13, 29), g.go(['CERULEAN_CITY_BIKE_SHOP'], rec), g.explore(rec)))
    print(g.k, g.pos(), 'hm01', g.getflag(0x237), 'voucher', g.getflag(0x241), 'bike', g.getflag(0x271), flush=True)
run_segment('s17b_captain', 's17_vermilion', go)
