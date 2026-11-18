import sys; sys.path.insert(0, "/home/claude/tools")
from story import *
def go(g, rec):
    g.handle(); g.trail = []
    step(g, rec, 'miguel', lambda: (tp(g, rec, 'MT_MOON_B2F', 14, 13), walk(g, rec, 14, 11), g.handle(rec)))
    step(g, rec, 'fossil', lambda: talk(g, rec, 13, 7, 'dome fossil'))
    step(g, rec, 'cerulean', lambda: (tp(g, rec, 'CERULEAN_CITY', 22, 20), g.explore(rec)))
    for h in ['CERULEAN_CITY_POKEMON_CENTER_1F', 'CERULEAN_CITY_HOUSE1', 'CERULEAN_CITY_HOUSE3', 'CERULEAN_CITY_HOUSE4', 'CERULEAN_CITY_HOUSE5', 'CERULEAN_CITY_MART', 'CERULEAN_CITY_BIKE_SHOP']:
        step(g, rec, h, lambda h=h: visit(g, rec, h, 'CERULEAN_CITY'))
    step(g, rec, 'rival', lambda: (walk(g, rec, 23, 7), walk(g, rec, 23, 6), g.handle(rec)))
    step(g, rec, 'bridge', lambda: (tp(g, rec, 'ROUTE24', 11, 33), walk(g, rec, 11, 15), g.handle(rec), walk(g, rec, 11, 10)))
    step(g, rec, 'route24', lambda: g.explore(rec))
    step(g, rec, 'route25', lambda: (tp(g, rec, 'ROUTE25', 12, 6), g.explore(rec)))
    step(g, rec, 'cottage', lambda: (tp(g, rec, 'ROUTE25', 51, 5), g.go(['ROUTE25_SEA_COTTAGE'], rec)))
    step(g, rec, 'bill1', lambda: talk(g, rec, 10, 6, 'bill clefairy'))
    step(g, rec, 'billpc', lambda: talk(g, rec, 4, 5, 'bill pc'))
    step(g, rec, 'bill2', lambda: (g.run(120), g.handle(rec), g.explore(rec)))
    step(g, rec, 'gym', lambda: (tp(g, rec, 'CERULEAN_CITY', 31, 22), g.go(['CERULEAN_CITY_GYM'], rec), g.explore(rec)))
    step(g, rec, 'heal', lambda: (tp(g, rec, 'CERULEAN_CITY', 22, 20), g.go(['CERULEAN_CITY_POKEMON_CENTER_1F'], rec), g.heal_center(rec)))
    step(g, rec, 'house2', lambda: (tp(g, rec, 'CERULEAN_CITY', 30, 12), g.go(['CERULEAN_CITY_HOUSE2'], rec), g.explore(rec)))
    step(g, rec, 'grunt', lambda: (tp(g, rec, 'CERULEAN_CITY', 31, 9), walk(g, rec, 33, 7), g.handle(rec)))
    print(g.k, g.pos(), 'badge2', g.getflag(0x821), 'ticket?', flush=True)
run_segment('s16_cerulean', 's15_mtmoon', go)
