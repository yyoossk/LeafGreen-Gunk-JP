import sys; sys.path.insert(0, "/home/claude/tools")
from story import *
def go(g, rec):
    g.handle(); g.trail = []; power_up(g)
    step(g, rec, 'bike', lambda: (tp(g, rec, 'CERULEAN_CITY_BIKE_SHOP', 9, 4), talk(g, rec, 9, 3, 'bike clerk')))
    step(g, rec, 'route9', lambda: (tp(g, rec, 'ROUTE9', 8, 8), g.explore(rec)))
    step(g, rec, 'route10pc', lambda: (tp(g, rec, 'ROUTE10', 13, 21), g.go(['ROUTE10_POKEMON_CENTER_1F'], rec), g.explore(rec)))
    step(g, rec, 'lavender', lambda: (tp(g, rec, 'LAVENDER_TOWN', 6, 6), g.explore(rec)))
    for h in ['LAVENDER_TOWN_POKEMON_CENTER_1F', 'LAVENDER_TOWN_VOLUNTEER_POKEMON_HOUSE', 'LAVENDER_TOWN_HOUSE1', 'LAVENDER_TOWN_HOUSE2', 'LAVENDER_TOWN_MART']:
        step(g, rec, h, lambda h=h: visit(g, rec, h, 'LAVENDER_TOWN'))
    step(g, rec, 'route8', lambda: (tp(g, rec, 'ROUTE8', 10, 9), g.explore(rec)))
    step(g, rec, 'route7', lambda: (tp(g, rec, 'ROUTE7', 10, 10), g.explore(rec)))
    step(g, rec, 'celadon', lambda: (tp(g, rec, 'CELADON_CITY', 48, 12), g.explore(rec)))
    for h in ['CELADON_CITY_POKEMON_CENTER_1F', 'CELADON_CITY_CONDOMINIUMS_1F', 'CELADON_CITY_RESTAURANT', 'CELADON_CITY_HOUSE1', 'CELADON_CITY_HOTEL', 'CELADON_CITY_GAME_CORNER_PRIZE_ROOM', 'CELADON_CITY_DEPARTMENT_STORE_1F']:
        step(g, rec, h, lambda h=h: visit(g, rec, h, 'CELADON_CITY'))
    for f in ['CELADON_CITY_DEPARTMENT_STORE_2F', 'CELADON_CITY_DEPARTMENT_STORE_3F', 'CELADON_CITY_DEPARTMENT_STORE_4F', 'CELADON_CITY_DEPARTMENT_STORE_5F', 'CELADON_CITY_DEPARTMENT_STORE_ROOF', 'CELADON_CITY_CONDOMINIUMS_2F', 'CELADON_CITY_CONDOMINIUMS_3F', 'CELADON_CITY_CONDOMINIUMS_ROOF']:
        step(g, rec, f, lambda f=f: (tp(g, rec, f, *{'CELADON_CITY_DEPARTMENT_STORE_ROOF': (14, 6), 'CELADON_CITY_CONDOMINIUMS_ROOF': (6, 6)}.get(f, (6, 3))), g.explore(rec)))
    step(g, rec, 'gamecorner', lambda: (tp(g, rec, 'CELADON_CITY', 34, 22), g.go(['CELADON_CITY_GAME_CORNER'], rec), g.explore(rec)))
    step(g, rec, 'giovanni', lambda: (tp(g, rec, 'ROCKET_HIDEOUT_B4F', 19, 7), talk(g, rec, 19, 4, 'giovanni'), g.handle(rec), talk(g, rec, 20, 5, 'silph scope')))
    step(g, rec, 'erika', lambda: (tp(g, rec, 'CELADON_CITY_GYM', 6, 5), talk(g, rec, 6, 4, 'erika')))
    step(g, rec, 'tower', lambda: (tp(g, rec, 'LAVENDER_TOWN', 18, 7), g.go(['POKEMON_TOWER_1F'], rec), g.explore(rec)))
    step(g, rec, 'tower2f', lambda: (tp(g, rec, 'POKEMON_TOWER_2F', 17, 7), walk(g, rec, 17, 5), g.handle(rec), g.explore(rec)))
    step(g, rec, 'marowak', lambda: (tp(g, rec, 'POKEMON_TOWER_6F', 11, 13), walk(g, rec, 11, 15), g.handle(rec)))
    step(g, rec, 'tower7f', lambda: (tp(g, rec, 'POKEMON_TOWER_7F', 11, 15), g.explore(rec)))
    step(g, rec, 'fuji', lambda: (g.handle(rec), g.pos()[2:] == mapid('LAVENDER_TOWN_VOLUNTEER_POKEMON_HOUSE') or tp(g, rec, 'LAVENDER_TOWN_VOLUNTEER_POKEMON_HOUSE', 3, 5), talk(g, rec, 3, 3, 'fuji')))
    print(g.k, g.pos(), 'bike', g.getflag(0x271), 'badge4', g.getflag(0x823), 'tea', g.getflag(0x2A6), 'fuji', g.getflag(0x23C), 'flute', g.getflag(0x23D), flush=True)
run_segment('s18_celadon', 's17b_captain', go)
