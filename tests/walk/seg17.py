import sys; sys.path.insert(0, "/home/claude/tools")
from story import *
def go(g, rec):
    g.handle(); g.trail = []
    step(g, rec, 'route5', lambda: (tp(g, rec, 'ROUTE5', 14, 20), g.explore(rec)))
    step(g, rec, 'route6', lambda: (tp(g, rec, 'ROUTE6', 12, 8), g.explore(rec)))
    step(g, rec, 'vermilion', lambda: (tp(g, rec, 'VERMILION_CITY', 15, 7), g.explore(rec)))
    for h in ['VERMILION_CITY_POKEMON_CENTER_1F', 'VERMILION_CITY_HOUSE1', 'VERMILION_CITY_POKEMON_FAN_CLUB', 'VERMILION_CITY_HOUSE2', 'VERMILION_CITY_MART', 'VERMILION_CITY_HOUSE3']:
        step(g, rec, h, lambda h=h: visit(g, rec, h, 'VERMILION_CITY'))
    step(g, rec, 'ticket', lambda: (walk(g, rec, 23, 31), walk(g, rec, 23, 33), g.handle(rec), g.go(['SSANNE_EXTERIOR'], rec)))
    step(g, rec, 'ssanne1f', lambda: (g.go(['SSANNE_1F_CORRIDOR'], rec), g.explore(rec)))
    step(g, rec, 'rival', lambda: (tp(g, rec, 'SSANNE_2F_CORRIDOR', 31, 8), walk(g, rec, 31, 6), g.handle(rec)))
    step(g, rec, 'captain', lambda: (g.go(['SSANNE_CAPTAINS_OFFICE'], rec), g.explore(rec)))
    step(g, rec, 'leave', lambda: (tp(g, rec, 'SSANNE_1F_CORRIDOR', 0, 0) if False else None, tp(g, rec, 'SSANNE_EXTERIOR', 32, 7), walk(g, rec, 32, 6), g.go(['VERMILION_CITY'], rec), g.handle(rec)))
    step(g, rec, 'gym', lambda: (tp(g, rec, 'VERMILION_CITY', 14, 26), g.go(['VERMILION_CITY_GYM'], rec), g.explore(rec)))
    step(g, rec, 'surge', lambda: (g.getflag(0x822) or (tp(g, rec, 'VERMILION_CITY_GYM', 5, 4), talk(g, rec, 5, 2, 'surge'))))
    step(g, rec, 'route11', lambda: (tp(g, rec, 'ROUTE11', 10, 8), g.explore(rec)))
    step(g, rec, 'aide', lambda: (tp(g, rec, 'ROUTE11', 58, 11), g.go(['ROUTE11_EAST_ENTRANCE_1F'], rec), g.explore(rec), g.go(['ROUTE11_EAST_ENTRANCE_2F'], rec), g.explore(rec)))
    step(g, rec, 'diglett', lambda: (tp(g, rec, 'DIGLETTS_CAVE_B1F', 82, 70), g.explore(rec)))
    step(g, rec, 'route2', lambda: (tp(g, rec, 'ROUTE2', 17, 23), g.go(['ROUTE2_HOUSE'], rec), g.explore(rec), tp(g, rec, 'ROUTE2', 18, 47), g.go(['ROUTE2_EAST_BUILDING'], rec), g.explore(rec)))
    print(g.k, g.pos(), 'ticket', g.getflag(0x234), 'hm01', g.getflag(0x237), 'badge3', g.getflag(0x822), 'voucher', g.getflag(0x241), flush=True)
run_segment('s17_vermilion', 's16_cerulean', go)
