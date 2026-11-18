#!/usr/bin/env python3
# 151匹揃う版: feature tests on /home/claude/work/port151.gba (teleport via a RAM script)
import sys, struct, os, json
sys.path.insert(0, '/home/claude/tools')
import walker
from walker import Game, mapid
ROM = '/home/claude/work/port151.gba'
SCR = 0x02021E88   # inside gStringVar4 (only needs to live for one frame)
OUT = '/tmp/t151'; os.makedirs(OUT, exist_ok=True)

def poke(g, a, data):
    for i, b in enumerate(data): g.cmd(f'poke {a + i:08X} {b:02X}')

def teleport(g, name, x, y):
    grp, num = mapid(name)
    poke(g, SCR, bytes([0x39, grp, num, 0xFF]) + struct.pack('<hh', x, y) + b'\x02')
    poke(g, 0x03000EB1, b'\x01')                       # mode = bytecode
    poke(g, 0x03000EB0, b'\x00')                       # stack depth
    poke(g, 0x03000EB8, struct.pack('<I', SCR))        # scriptPtr
    poke(g, 0x03000EA8, b'\x00')                       # status = running
    for i in range(40):
        g.run(20)
        if g.pos()[2:] == (grp, num) and g.idle(): break
    g.run(90)
    return g.pos()

def sb1(g): return g.u32(0x03004FA8)
def setflag(g, f, on=True):
    a = sb1(g) + 0xEE0 + f // 8; v = g.u8(a)
    poke(g, a, bytes([(v | (1 << (f % 8))) if on else (v & ~(1 << (f % 8)))]))
def getflag(g, f): return (g.u8(sb1(g) + 0xEE0 + f // 8) >> (f % 8)) & 1
def setvar(g, v, val): poke(g, sb1(g) + 0x1000 + 2 * (v - 0x4000), struct.pack('<H', val))
def getvar(g, v): return g.u16(sb1(g) + 0x1000 + 2 * (v - 0x4000))
def count(g): return g.u8(0x02023F89)
def setcount(g, n): poke(g, 0x02023F89, bytes([n]))
def species(g, slot):
    import mkmon
    d = g.peek(0x020241E4 + 100 * slot, 100)
    return mkmon.species_of(d) if hasattr(mkmon, 'species_of') else None

def talk(g, x, y, shots, tag, first='A', then='B', n=40):
    """walk next to (x,y), face, press A; mash `first` until the party count changes, then `then`"""
    r = g.goto(x, y, adj=True)
    px, py, _, _ = g.pos()
    d = {(1, 0): 'R', (-1, 0): 'L', (0, 1): 'D', (0, -1): 'U'}.get((x - px, y - py))
    if d: g.face(d)
    c0 = count(g); key = first
    g.tap('A'); g.run(20)
    if g.idle() and d:
        g.face(d); g.tap('A'); g.run(20)
    for i in range(n):
        if i < 14 or i % 5 == 0: shots.append(snap(g, f'{tag}_{i:02d}'))
        if g.in_battle(): return 'battle'
        if count(g) != c0: key = then
        if g.idle():
            g.run(20)
            if g.idle(): break
        g.tap(key); g.run(6)
    shots.append(snap(g, f'{tag}_end'))
    return 'idle'

def snap(g, tag):
    f = f'{OUT}/{tag}.png'; g.shot(f); return f
