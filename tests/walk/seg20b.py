import sys; sys.path.insert(0, "/home/claude/tools")
from story import *
def go(g, rec):
    g.handle(); g.trail = []; power_up(g)
    step(g, rec, 'indigo', lambda: (tp(g, rec, 'INDIGO_PLATEAU_POKEMON_CENTER_1F', 11, 14), g.heal_center(rec)))
    rooms = [('POKEMON_LEAGUE_LORELEIS_ROOM', (6, 5)), ('POKEMON_LEAGUE_BRUNOS_ROOM', (6, 5)), ('POKEMON_LEAGUE_AGATHAS_ROOM', (6, 5)), ('POKEMON_LEAGUE_LANCES_ROOM', (6, 8))]
    for room, npc in rooms:
        step(g, rec, room, lambda room=room, npc=npc: (tp(g, rec, room, npc[0] - 1, npc[1]), g.face('R'), g.tap('A'), g.run(30), g.handle(rec), rec.append((room, [g.snap()]))))
    step(g, rec, 'champion', lambda: (tp(g, rec, 'POKEMON_LEAGUE_LANCES_ROOM', 6, 7), walk(g, rec, 6, 5), g.handle(rec), g.go(['POKEMON_LEAGUE_CHAMPIONS_ROOM'], rec), g.handle(rec)))
    for i in range(30):
        if g.getflag(0x82C): break
        g.handle(rec); g.tap('A'); g.run(60)
    rec.append(('after champion', [g.snap('hof')]))
    for i in range(400):                      # Hall of Fame + credits
        g.tap('A'); g.run(30)
        if i % 40 == 0: rec.append((f'credits {i}', [g.snap('credits')]))
    print(g.k, g.pos(), 'clear', g.getflag(0x82C), flush=True)
run_segment('s20b_e4', 's20_league', go)
