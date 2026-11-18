import sys; sys.path.insert(0, "/home/claude/tools")
from story import *
def e4(g, rec, room, nx, ny, npc):
    tp(g, rec, room, 6, 7 if npc[1] == 5 else 10)
    talk(g, rec, npc[0], npc[1], room)
    g.handle(rec)
def go(g, rec):
    g.handle(); g.trail = []; power_up(g)
    step(g, rec, 'president', lambda: (tp(g, rec, 'SILPH_CO_11F', 9, 10), talk(g, rec, 9, 9, 'president')))
    step(g, rec, 'cinnabar', lambda: (tp(g, rec, 'CINNABAR_ISLAND', 14, 12), g.explore(rec)))
    for h in ['CINNABAR_ISLAND_POKEMON_CENTER_1F', 'CINNABAR_ISLAND_MART', 'CINNABAR_ISLAND_POKEMON_LAB_ENTRANCE']:
        step(g, rec, h, lambda h=h: visit(g, rec, h, 'CINNABAR_ISLAND'))
    for r in ['CINNABAR_ISLAND_POKEMON_LAB_LOUNGE', 'CINNABAR_ISLAND_POKEMON_LAB_RESEARCH_ROOM', 'CINNABAR_ISLAND_POKEMON_LAB_EXPERIMENT_ROOM']:
        step(g, rec, r, lambda r=r: (tp(g, rec, r, 7 if 'EXPERIMENT' in r else 5, 7), g.explore(rec)))
    step(g, rec, 'mansion', lambda: (tp(g, rec, 'POKEMON_MANSION_1F', 5, 26), g.explore(rec)))
    step(g, rec, 'secretkey', lambda: (tp(g, rec, 'POKEMON_MANSION_B1F', 5, 8), talk(g, rec, 5, 7, 'secret key'), talk(g, rec, 21, 27, 'diary(mew)')))
    step(g, rec, 'blaine', lambda: (tp(g, rec, 'CINNABAR_ISLAND_GYM', 5, 6), talk(g, rec, 5, 4, 'blaine')))
    step(g, rec, 'viridian', lambda: (tp(g, rec, 'VIRIDIAN_CITY_GYM', 2, 4), talk(g, rec, 2, 2, 'giovanni')))
    step(g, rec, 'rival22', lambda: (tp(g, rec, 'ROUTE22', 35, 5), walk(g, rec, 33, 5), g.handle(rec)))
    for (x, y) in [(13, 149), (7, 140), (12, 123), (11, 111), (9, 94), (12, 61), (1, 35)]:
        step(g, rec, f'guard{y}', lambda x=x, y=y: (tp(g, rec, 'ROUTE23', x, y + 1), walk(g, rec, x, y), g.handle(rec)))
    step(g, rec, 'victoryroad', lambda: (tp(g, rec, 'VICTORY_ROAD_1F', 11, 19), g.explore(rec)))
    step(g, rec, 'indigo', lambda: (tp(g, rec, 'INDIGO_PLATEAU_EXTERIOR', 11, 8), g.go(['INDIGO_PLATEAU_POKEMON_CENTER_1F'], rec), g.heal_center(rec), g.explore(rec)))
    step(g, rec, 'lorelei', lambda: e4(g, rec, 'POKEMON_LEAGUE_LORELEIS_ROOM', 6, 7, (6, 5)))
    step(g, rec, 'bruno', lambda: e4(g, rec, 'POKEMON_LEAGUE_BRUNOS_ROOM', 6, 7, (6, 5)))
    step(g, rec, 'agatha', lambda: e4(g, rec, 'POKEMON_LEAGUE_AGATHAS_ROOM', 6, 7, (6, 5)))
    step(g, rec, 'lance', lambda: e4(g, rec, 'POKEMON_LEAGUE_LANCES_ROOM', 6, 10, (6, 8)))
    step(g, rec, 'champion', lambda: (walk(g, rec, 6, 5), g.handle(rec)))
    print(g.k, g.pos(), 'badges', [g.getflag(0x820 + i) for i in range(8)], 'clear', g.getflag(0x82C), flush=True)
run_segment('s20_league', 's19_saffron', go)
