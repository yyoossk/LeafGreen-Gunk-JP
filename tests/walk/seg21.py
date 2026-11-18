import sys; sys.path.insert(0, "/home/claude/tools")
from story import *
def boot(g, rec):
    g.cmd('reset')
    for i in range(60):
        g.run(30); g.tap('A')
        if g.in_overworld() and g.idle(): break
    g.run(60); rec.append(('continue after HoF', [g.snap('cont')]))
    return g.pos()
def go(g, rec):
    g.handle()
    g.handle(); g.trail = []; power_up(g)
    step(g, rec, 'pallet', lambda: (g.explore(rec), tp(g, rec, 'PALLET_TOWN_PROFESSOR_OAKS_LAB', 6, 10), g.explore(rec)))
    step(g, rec, 'tmshop', lambda: (tp(g, rec, 'CELADON_CITY_DEPARTMENT_STORE_2F', 3, 6), talk(g, rec, 1, 6, 'TM clerk (post-HoF)'), g.tap('B'), g.tap('B'), g.handle(rec)))
    step(g, rec, 'bill', lambda: (tp(g, rec, 'CINNABAR_ISLAND', 20, 8), talk(g, rec, 20, 7, 'bill cinnabar'), g.handle(rec)))
    step(g, rec, 'oneisland', lambda: (g.pos()[2:] == mapid('ONE_ISLAND_POKEMON_CENTER_1F') or tp(g, rec, 'ONE_ISLAND_POKEMON_CENTER_1F', 13, 7), g.handle(rec), talk(g, rec, 15, 6, 'celio'), g.explore(rec)))
    step(g, rec, 'one_town', lambda: (tp(g, rec, 'ONE_ISLAND', 14, 6), g.explore(rec)))
    step(g, rec, 'ember_rockets', lambda: (tp(g, rec, 'MT_EMBER_EXTERIOR', 38, 44), walk(g, rec, 38, 43), g.handle(rec), talk(g, rec, 41, 40, 'ember grunt1'), g.handle(rec), talk(g, rec, 42, 40, 'ember grunt2'), g.handle(rec)))
    step(g, rec, 'ruby', lambda: (tp(g, rec, 'MT_EMBER_RUBY_PATH_B5F', 7, 8), talk(g, rec, 7, 7, 'ruby')))
    step(g, rec, 'celio_ruby', lambda: (tp(g, rec, 'ONE_ISLAND_POKEMON_CENTER_1F', 15, 7), talk(g, rec, 15, 6, 'celio ruby'), g.handle(rec)))
    step(g, rec, 'icefall', lambda: (tp(g, rec, 'FOUR_ISLAND_ICEFALL_CAVE_BACK', 12, 20), walk(g, rec, 12, 18), g.handle(rec)))
    step(g, rec, 'sapphire', lambda: (tp(g, rec, 'SIX_ISLAND_DOTTED_HOLE_SAPPHIRE_ROOM', 7, 8), talk(g, rec, 7, 7, 'sapphire'), g.handle(rec)))
    step(g, rec, 'warehouse', lambda: (tp(g, rec, 'FIVE_ISLAND_ROCKET_WAREHOUSE', 23, 13), walk(g, rec, 23, 11), g.handle(rec), talk(g, rec, 27, 16, 'admin1'), g.handle(rec), talk(g, rec, 27, 4, 'gideon'), g.handle(rec)))
    step(g, rec, 'celio_sapphire', lambda: (tp(g, rec, 'ONE_ISLAND_POKEMON_CENTER_1F', 15, 7), talk(g, rec, 15, 6, 'celio sapphire'), g.handle(rec)))
    for isl, xy in [('TWO_ISLAND', (21, 8)), ('THREE_ISLAND', (14, 28)), ('FOUR_ISLAND', (18, 21)), ('FIVE_ISLAND', (18, 7)), ('SIX_ISLAND', (11, 12)), ('SEVEN_ISLAND', (12, 4))]:
        step(g, rec, isl, lambda isl=isl, xy=xy: (tp(g, rec, isl, *xy), g.explore(rec)))
    step(g, rec, 'seven_house', lambda: (visit(g, rec, 'SEVEN_ISLAND_HOUSE_ROOM1'), tp(g, rec, 'SEVEN_ISLAND_HOUSE_ROOM2', 4, 7), g.explore(rec)))
    step(g, rec, 'mewtwo', lambda: (tp(g, rec, 'CERULEAN_CAVE_B1F', 7, 13), g.explore(rec)))
    print(g.k, g.pos(), 'clear', g.getflag(0x82C), flush=True)
run_segment('s21_postgame', 's20b_e4', go)
