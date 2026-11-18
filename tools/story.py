# helpers for the story walkthrough segments (teleport between event spots, then play the event normally)
import sys; sys.path.insert(0, '/home/claude/tools')
from playtest import *
import walker

def step(g, rec, label, fn):
    try:
        r = fn()
        print('  ok', label, r, g.pos(), flush=True)
    except Exception as e:
        rec.append((f'ERROR {label} {e!r}', [g.snap('error')])); print('  ERR', label, repr(e), flush=True)

def tp(g, rec, name, x, y):
    p = g.teleport(name, x, y)
    if not g.idle(): g.handle(rec)
    return p

def talk(g, rec, x, y, label):
    return g.interact(x, y, label, rec, key='A')

def walk(g, rec, x, y):
    r = g.goto(x, y)
    for i in range(5):
        if g.idle(): break
        g.handle(rec)
        r = g.goto(x, y)
    return r

import json as _json, re as _re2
def _pretname(name):
    for l in open('/home/claude/pret/include/constants/map_groups.h'):
        pass
    import glob
    for f in glob.glob('/home/claude/pret/data/maps/*/map.json'):
        j = _json.load(open(f))
        if j['id'] == 'MAP_' + name: return j
def visit(g, rec, house, back=None):
    """teleport just inside a building's entrance and explore it"""
    j = _pretname(house); w = j['warp_events'][0]
    tp(g, rec, house, w['x'], w['y'] - 1); g.explore(rec)

def heal(g, rec, center, town):
    g.go([center], rec); g.heal_center(rec); g.go([town], rec)

import mkmon
def power_up(g):
    """test cheat (both versions): a fresh Lv100 MEWTWO (full PP) in slot 1, other party members kept"""
    P = g.R['party']; n = g.u8(g.R['cnt'])
    pt = g.party()
    own = g.peek(P + 100 * (1 if pt and pt[0]['species'] == 150 else 0), 100)   # the player's own mon: its OT id / name
    otid = struct.unpack_from('<I', own, 4)[0]
    m = bytearray(mkmon.mon(150, level=100, nick='ミュウツー', pid=0x7777, otid=otid, moves=(94, 57, 58, 85)))
    m[20:27] = own[20:27]; m = bytes(m)          # same OT name too, so it obeys
    if pt and pt[0]['species'] == 150:
        slots = [g.peek(P + 100 * i, 100) for i in range(1, n)]
    else:
        slots = [g.peek(P + 100 * i, 100) for i in range(n)][:5]
    data = m + b''.join(slots)
    for i, b in enumerate(data): g.cmd(f'poke {P + i:08X} {b:02X}')
    g.cmd(f'poke {g.R["cnt"]:08X} {1 + len(slots):02X}')
    g.boost()

_step0 = step
def step(g, rec, label, fn):
    g.boost()          # keeps the repel counter up (no wild battles) and stats at 999
    return _step0(g, rec, label, fn)
