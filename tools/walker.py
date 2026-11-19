#!/usr/bin/env python3
# Interactive play bot for the JP port (and the EN Gunk original) on top of gbarun.
# Reads RAM for position / map / collision / objects / battle state, walks with BFS, mashes text, fights.
import subprocess, struct, os, collections, time

ROMS = {
    'jp': dict(rom=os.environ.get('WALK_ROM','/home/claude/work/port.gba'), strbuf=0x02021C88, sb1=0x03004FA8, vmap=0x03004FE0, main=0x03003090, mapheader=0x02036D30,
               objs=0x02036D6C, avatar=0x02036FAC, ctx=0x03000EA8, battlecb=0x0801092D, owcb=0x08055E51,
               party=0x020241E4, cnt=0x02023F89, bmons=0x02023B44, bcf=0x03004F80, moves=0x08208E00, act=0x0802DB81, mv=0x0802E159, tgt=0x0802DDBD, fade=0x020379EC, btype=0x02022AAC, outcome=0x02023DEA),
    'en': dict(rom='/home/claude/gunk_en/pokeleafgreen_release.gba', strbuf=0x02021D18, sb1=0x03005008, vmap=0x03005040, main=0x030030F0, mapheader=0x02036E14,
               objs=0x02036E50, avatar=0x02037090, ctx=0x03000EA8, battlecb=0x08011199, owcb=0x08056A55,
               party=0x02024284, cnt=0x02024029, bmons=0x02023be4, bcf=0x03004FE0, moves=0x08252D08, act=0x0802E565, mv=0x0802EB85, tgt=0x0802E7E9, fade=0x02037B40, btype=0x02022B4C, outcome=0x02023E8A),
}
ROMS['fp'] = dict(rom='/home/claude/frlgplus/pokeleafgreen.gba', strbuf=0x02021C98, sb1=0x0300500C, vmap=0x03005040, main=0x030030F0, mapheader=0x02036F18,
               objs=0x02036F58, avatar=0x02037198, ctx=0x03000EA8, battlecb=0x080116B5, owcb=0x080598E1,
               party=0x02024204, cnt=0x02023FA9, bmons=0x02023B64, bcf=0x03004FE0, moves=0x082788B0, act=0x0802F4A9, mv=0x0802FAE1, tgt=0x0802F745, fade=0x02037BD8, btype=0x02022ACC, outcome=0x02023E0A)
DIRS = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}

class Game:
    def __init__(self, k, state=None, rom=None):
        self.k = k; self.R = dict(ROMS[k])
        if rom: self.R['rom'] = rom
        self.romdata = open(self.R['rom'], 'rb').read()
        self.p = subprocess.Popen(['/home/claude/emu/gbarun', self.R['rom'], '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        if state: self.cmd(f'ls {state}')
        self.frames = 0; self.log = []
    def cmd(self, s): self.p.stdin.write(s + '\n')
    def peek(self, a, n):
        self.cmd(f'peek {a:08X} {n}'); self.p.stdin.flush()
        l = self.p.stdout.readline()
        return bytes(int(x, 16) for x in l.split(':')[1].split())
    def u8(self, a): return self.peek(a, 1)[0]
    def u16(self, a): return struct.unpack('<H', self.peek(a, 2))[0]
    def u32(self, a): return struct.unpack('<I', self.peek(a, 4))[0]
    def run(self, n): self.cmd(f'run {n}'); self.frames += n
    def tap(self, k, n=1): self.cmd(f'tap {k} {n}'); self.frames += 16 * n
    def hold(self, k, n): self.cmd(f'hold {k} {n}'); self.frames += n
    def shot(self, f): self.cmd(f'shot {f}')
    def save(self, f): self.cmd(f'ss {f}')
    def close(self):
        try: self.p.stdin.close(); self.p.wait(5)
        except Exception: self.p.kill()
    # ---- state
    def sb1(self): return self.u32(self.R['sb1'])
    def pos(self):
        b = self.peek(self.sb1(), 6); x, y, g, n = struct.unpack('<hhbb', b); return x, y, g & 0xFF, n & 0xFF
    def cb2(self): return self.u32(self.R['main'] + 4)
    def in_battle(self): return self.cb2() == self.R['battlecb']
    def in_overworld(self): return self.cb2() == self.R['owcb']
    def script_running(self): return self.u8(self.R['ctx']) != 2
    def fading(self): return self.u8(self.R['fade'] + 7) & 0x80 != 0
    def facing(self):
        o = self.R['objs']  # player object is gObjectEvents[gPlayerAvatar.objectEventId]
        oid = self.u8(self.R['avatar'] + 5)
        return self.u8(o + 0x24 * oid + 0x18) & 0x0F
    def idle(self):
        return self.in_overworld() and not self.script_running() and not self.fading()
    # ---- map
    def grid(self):
        for t in range(20):
            try: return self._grid()
            except Exception:
                self.run(20)
        return self._grid()
    def _grid(self):
        w, h, mp = struct.unpack('<iiI', self.peek(self.R['vmap'], 12))
        raw = b''
        for i in range(0, w * h * 2, 1024): raw += self.peek(mp + i, min(1024, w * h * 2 - i))
        cells = struct.unpack(f'<{w*h}H', raw)
        lay = self.u32(self.R['mapheader'])
        pt, st = struct.unpack('<II', self.romdata[lay - 0x08000000 + 16: lay - 0x08000000 + 24])
        def attrs(ts): return struct.unpack('<I', self.romdata[ts - 0x08000000 + 20: ts - 0x08000000 + 24])[0]
        pa, sa = attrs(pt), attrs(st)
        def beh(m):
            a = pa + 4 * m if m < 640 else sa + 4 * (m - 640)
            return struct.unpack('<I', self.romdata[a - 0x08000000: a - 0x08000000 + 4])[0] & 0x1FF
        return w, h, cells, beh
    def objects(self):
        out = []
        b = self.peek(self.R['objs'], 0x24 * 16)
        for i in range(16):
            e = b[0x24 * i: 0x24 * i + 0x24]
            if e[0] & 1 and not (e[1] & 0x20):            # active and not invisible
                x, y = struct.unpack('<hh', e[0x10:0x14])
                out.append((i, x - 7, y - 7, e[5], e[8]))     # id, x, y, gfx, localId
        return out
    # ---- movement
    WATER = set(range(0x10, 0x18)) | {0x1A, 0x1B, 0x15}
    LEDGE = {0x38: 'R', 0x39: 'L', 0x3A: 'U', 0x3B: 'D'}
    def path(self, tx, ty, adj=False, avoid_grass=False):
        x0, y0, g, n = self.pos()
        w, h, cells, beh = self.grid()
        objs = {(o[1], o[2]) for o in self.objects()[1:]} if True else set()
        player_oid = self.u8(self.R['avatar'] + 5)
        objs = {(o[1], o[2]) for o in self.objects() if o[0] != player_oid and o[4] != 254}
        if getattr(self, 'avoid_coords', False):
            try: objs |= {(c['x'], c['y']) for c in self.events()['coords']} - {(tx, ty)}
            except Exception: pass
        mw, mh = self.mapsize()
        def ok(x, y, d):
            if not (0 <= x < mw and 0 <= y < mh): return False
            c = cells[(y + 7) * w + x + 7]
            if c & 0x0C00: return False
            if (x, y) in objs: return False
            b = beh(c & 0x3FF)
            if b in self.WATER: return False
            if avoid_grass and b == 0x02: return 2
            return True
        start = (x0, y0); goal = (tx, ty)
        prev = {start: None}; q = collections.deque([start])
        while q:
            cur = q.popleft()
            if (adj and abs(cur[0] - tx) + abs(cur[1] - ty) == 1) or (not adj and cur == goal): break
            for d, (dx, dy) in DIRS.items():
                nx, ny = cur[0] + dx, cur[1] + dy
                if (nx, ny) in prev: continue
                if not (0 <= nx + 7 < w and 0 <= ny + 7 < h): continue
                c = cells[(ny + 7) * w + nx + 7]
                b = beh(c & 0x3FF)
                if b in self.LEDGE:
                    if self.LEDGE[b] != d: continue
                    jx, jy = nx + dx, ny + dy
                    if (jx, jy) in prev or not ok(jx, jy, d): continue
                    prev[(jx, jy)] = (cur, d); q.append((jx, jy)); continue
                if (nx, ny) == goal and not adj:
                    prev[(nx, ny)] = (cur, d); q.append((nx, ny)); continue
                if not ok(nx, ny, d): continue
                prev[(nx, ny)] = (cur, d); q.append((nx, ny))
        else:
            return None
        steps = []; c = cur
        while prev[c]: c, d = prev[c][0], prev[c][1]; steps.append(d)
        return steps[::-1], cur
    def step(self, d):
        x, y, g, n = self.pos()
        self.hold(d, 16); self.run(2)
        return self.pos()[:2] != (x, y)
    def face(self, d):
        p0 = self.pos()
        self.hold(d, 3); self.run(10)
        if self.pos() != p0:   # moved instead of turning: step back
            back = {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}[d]
            self.hold(back, 16); self.run(4); self.hold(d, 3); self.run(10)
    def goto(self, tx, ty, adj=False, tries=30, handler=None):
        for t in range(tries):
            if handler and not self.idle(): handler(self)
            x, y, g, n = self.pos()
            if (not adj and (x, y) == (tx, ty)) or (adj and abs(x - tx) + abs(y - ty) == 1): return True
            r = self.path(tx, ty, adj)
            if not r: self.run(30); continue
            steps, _ = r
            for d in steps[:8]:
                before = self.pos()
                self.lastdir = d
                self.hold(d, 16); self.run(2)
                if not self.idle():
                    return 'event'
                if self.pos()[2:] != before[2:]: return 'warp'
        return False

def _events(self):
    hdr = self.R['mapheader']
    ev = self.u32(hdr + 4)
    b = self.peek(ev, 20)
    no, nw, nc, nb = b[0], b[1], b[2], b[3]
    po, pw, pc, pb = struct.unpack('<IIII', b[4:20])
    objs = []
    for i in range(no):
        e = self.peek(po + 24 * i, 24)
        lid, gfx = e[0], e[1]; x, y = struct.unpack('<hh', e[4:8]); scr = struct.unpack('<I', e[16:20])[0]; flag = struct.unpack('<H', e[20:22])[0]
        objs.append(dict(lid=lid, gfx=gfx, x=x, y=y, script=scr, flag=flag))
    warps = []
    for i in range(nw):
        e = self.peek(pw + 8 * i, 8); x, y = struct.unpack('<hh', e[:4]); warps.append(dict(x=x, y=y, warp=e[5], num=e[6], grp=e[7]))
    bgs = []
    for i in range(nb):
        e = self.peek(pb + 12 * i, 12); x, y = struct.unpack('<hh', e[:4]); bgs.append(dict(x=x, y=y, kind=e[5], data=struct.unpack('<I', e[8:12])[0]))
    coords = []
    for i in range(nc):
        e = self.peek(pc + 16 * i, 16); x, y = struct.unpack('<hh', e[:4]); coords.append(dict(x=x, y=y))
    return dict(objs=objs, warps=warps, bgs=bgs, coords=coords)
Game.events = _events

def _mapsize(self):
    w, h = struct.unpack('<ii', self.peek(self.R['vmap'], 8)); return w - 15, h - 14
Game.mapsize = _mapsize

def _mash(self, maxn=60, key='A', shots=None):
    """advance text / scripts until the player can move again (or a battle starts)"""
    for i in range(maxn):
        if self.in_battle(): return 'battle'
        if self.idle():
            self.run(10)
            if self.idle(): return 'idle'
        if shots is not None and i < 6: shots.append(self.snap())
        self.tap(key)
    return 'timeout'
Game.mash = _mash

_snapn = [0]
def _snap(self, tag=None):
    _snapn[0] += 1
    f = f'/tmp/walk/{self.k}_{_snapn[0]:05d}{"_" + tag if tag else ""}.png'
    os.makedirs('/tmp/walk', exist_ok=True); self.shot(f); return f
Game.snap = _snap

def _battle(self, log=None):
    """fight: mash A (FIGHT -> first move); stops when back on the field"""
    n = 0
    while not self.in_overworld() and n < 400:
        self.tap('A'); n += 1
        if n % 40 == 0 and log is not None: log.append(self.snap('battle'))
    for i in range(30):
        if self.idle(): break
        self.tap('A')
    return self.u8(self.R['outcome'])
Game.battle = _battle

def _interact(self, x, y, label, rec, key='B', approach=None):
    """walk next to (x,y), face it, press A, record the first screens, mash the rest"""
    r = self.goto(x, y, adj=True)
    if r == 'event' or r == 'warp' or not r:
        return r
    px, py, _, _ = self.pos()
    d = {(1, 0): 'R', (-1, 0): 'L', (0, 1): 'D', (0, -1): 'U'}[(x - px, y - py)]
    self.face(d)
    self.tap('A'); self.run(20)
    if self.idle():
        self.face(d); self.tap('A'); self.run(20)
    shots = [self.snap()]
    if self.in_battle():
        rec.append((label + ' (battle)', shots)); self.battle(shots); return 'battle'
    for i in range(3):
        if self.idle(): break
        self.tap(key); self.run(10); shots.append(self.snap())
    res = self.mash(key=key)
    if res == 'battle': self.battle(shots); res = 'battle'
    rec.append((label, shots))
    return res
Game.interact = _interact

def _explore(self, rec, skip_objs=(), skip_bgs=()):
    """talk to every NPC and check every sign / bg event on the current map"""
    ev = self.events()
    mp = self.pos()[2:]
    if not hasattr(self, 'done_bgs'): self.done_bgs = {}
    dbg = self.done_bgs.setdefault(mp, set())
    for i, b in enumerate(ev['bgs']):
        if i in skip_bgs or b['kind'] > 4 or i in dbg: continue
        if self.low(): self.heal_nearest(rec)
        if self.pos()[2:] != mp: break
        dbg.add(i)
        if self.pos()[2:] != mp: break
        self.interact(b['x'], b['y'], f"map{mp} bg{i} ({b['x']},{b['y']})", rec)
    oid = self.u8(self.R['avatar'] + 5)
    if not hasattr(self, 'done_objs'): self.done_objs = {}
    done = self.done_objs.setdefault(mp, set())
    for t in ev['objs']:
        if self.low():
            self.heal_nearest(rec)
            if self.pos()[2:] != mp: break
        if t['lid'] in skip_objs or t['lid'] in done: continue
        if self.pos()[2:] != mp: break
        live = [q for q in self.objects() if q[4] == t['lid'] and q[0] != oid]
        if not live:
            # walk towards the template so the object gets spawned
            r = self.travel(t['x'], t['y'], rec, adj=True)
            if self.pos()[2:] != mp: break
            live = [q for q in self.objects() if q[4] == t['lid'] and q[0] != oid]
            if not live: continue
        done.add(t['lid'])
        for attempt in range(3):
            live = [q for q in self.objects() if q[4] == t['lid'] and q[0] != oid]
            if not live: break
            r = self.interact(live[0][1], live[0][2], f"map{mp} obj{t['lid']} gfx{live[0][3]}", rec)
            if r in ('idle', 'battle'): break
            if not self.idle(): self.handle(rec)
Game.explore = _explore

def _warp_to(self, idx=None, grp=None, num=None):
    ev = self.events()
    w = [w for w in ev['warps'] if (grp is None or (w['grp'], w['num']) == (grp, num))]
    if idx is not None: w = [ev['warps'][idx]]
    if not w: return self.pos()
    W_, H_, cells_, beh_ = self.grid()
    def wb(q): return beh_(cells_[(q['y'] + 7) * W_ + q['x'] + 7] & 0x3FF)
    w.sort(key=lambda q: 0 if wb(q) else 1)
    w = w[0]
    arrow = {0x62: 'R', 0x63: 'L', 0x64: 'U', 0x65: 'D'}.get(wb(w))
    before = self.pos()[2:]
    r = self.travel(w['x'], w['y'])
    for i in range(10):
        self.run(20)
        if self.pos()[2:] != before and self.idle(): return self.pos()
    if self.pos()[2:] == before and self.pos()[:2] != (w['x'], w['y']):
        r = self.goto(w['x'], w['y'], adj=True)
    # doors/stairs: step onto / into the warp from the side we stand on, then try the other directions
    px, py = self.pos()[:2]
    first = {(1, 0): 'R', (-1, 0): 'L', (0, 1): 'D', (0, -1): 'U'}.get((w['x'] - px, w['y'] - py))
    if (px, py) == (w['x'], w['y']): first = arrow or getattr(self, 'lastdir', None)
    for d in ([first] if first else []) + ['U', 'D', 'L', 'R']:
        self.run(30)
        if self.pos()[2:] != before: break
        self.hold(d, 24); self.run(60)
        if self.pos()[2:] != before: break
    for i in range(10):
        self.run(20)
        if self.idle(): break
    return self.pos()
Game.warp_to = _warp_to

def compare(recs_en, recs_jp, out, maxshots=3):
    """side by side: EN left, JP right; one row per interaction"""
    from PIL import Image, ImageDraw
    rows = []
    je = {l: s for l, s in recs_jp}; ee = {l: s for l, s in recs_en}
    order = []
    for l, _ in recs_en + recs_jp:
        if l not in order: order.append(l)
    for l in order:
        se = ee.get(l, []); sj = je.get(l, [])
        n = max(len(se), len(sj)) if l.startswith(('oak event', 'event')) else min(maxshots, max(len(se), len(sj)))
        for c in range(0, max(n, 1), maxshots):
            rows.append((l if c == 0 else '', se[c:c + maxshots], sj[c:c + maxshots]))
    W = 240 * maxshots * 2 + 16
    im = Image.new('RGB', (W, len(rows) * 174 + 2), (30, 30, 30)); d = ImageDraw.Draw(im)
    for i, (l, se, sj) in enumerate(rows):
        y = i * 174
        d.text((2, y), l, fill=(255, 255, 0))
        for j, f in enumerate(se):
            try: im.paste(Image.open(f), (240 * j, y + 12))
            except Exception: pass
        for j, f in enumerate(sj):
            try: im.paste(Image.open(f), (240 * maxshots + 16 + 240 * j, y + 12))
            except Exception: pass
    im.save(out); return out

def _handle(self, rec=None):
    """deal with whatever interrupted walking: battle, text, warp fade"""
    if self.k == 'en':
        try: self.cmd(f'poke {self.sb1()+0x1000+2*0x20:08X} FA')
        except Exception: pass
    for i in range(200):
        if self.idle(): return
        if self.in_battle():
            shots = []
            self.battle(shots)
            if rec is not None: rec.append((f'battle at {self.pos()}', shots[:3]))
            continue
        self.tap('B')
Game.handle = _handle

def _travel(self, tx, ty, rec=None, adj=False):
    start_map = self.pos()[2:]
    for t in range(40):
        if self.pos()[2:] != start_map: return 'warp'
        r = self.goto(tx, ty, adj=adj)
        if r is True: return True
        if r in ('event',) or not self.idle(): self.handle(rec); continue
        if r == 'warp': return 'warp'
        if r is False: self.run(30)
    return False
Game.travel = _travel

def _edge(self, d, rec=None, prefer=None):
    """walk off the map edge in direction d (U/D/L/R) to the connected map"""
    mp = self.pos()[2:]
    w, h = self.mapsize()
    W, H, cells, beh = self.grid()
    def free(x, y):
        c = cells[(y + 7) * W + x + 7]
        return not (c & 0x0C00) and beh(c & 0x3FF) not in self.WATER
    if d in 'UD':
        y = 0 if d == 'U' else h - 1
        xs = [x for x in range(w) if free(x, y)]
        xs.sort(key=lambda x: abs(x - (prefer if prefer is not None else self.pos()[0])))
        cands = [(x, y) for x in xs]
    else:
        x = 0 if d == 'L' else w - 1
        ys = [y for y in range(h) if free(x, y)]
        ys.sort(key=lambda y: abs(y - (prefer if prefer is not None else self.pos()[1])))
        cands = [(x, y) for y in ys]
    for (x, y) in cands[:6]:
        if self.path(x, y) is None: continue
        for t in range(6):
            r = self.travel(x, y, rec)
            if r is True or self.pos()[:2] == (x, y): break
            if self.pos()[2:] != mp: return self.pos()
        if self.pos()[:2] == (x, y):
            for k in range(4):
                self.hold(d, 20); self.run(30)
                if self.pos()[2:] != mp:
                    self.run(30); return self.pos()
                if not self.idle(): self.handle(rec)
    return self.pos()
Game.edge = _edge

def _boost(self):
    """EN reference only: make the party unbeatable (level 100, 999 stats) so it never whites out"""
    n = self.u8(self.R['cnt'])
    sb = self.sb1()
    self.cmd(f'poke {sb+0x1000+2*0x20:08X} FA')   # VAR_REPEL_STEP_COUNT = 250 (EN reference: no wild battles)
    for s in range(n):
        b = self.R['party'] + 100 * s
        self.cmd(f'poke {b+84:08X} 64')
        for off in (86, 88, 90, 92, 94, 96, 98):
            self.cmd(f'poke {b+off:08X} E7'); self.cmd(f'poke {b+off+1:08X} 03')
Game.boost = _boost

def _low(self, ratio=0.4):
    if self.k == 'en' or getattr(self, '_healing', False): return False
    lv, hp, mx = self.hp()
    return mx and hp < mx * ratio
Game.low = _low

def _hp(self, slot=0):
    b = self.peek(self.R['party'] + 100 * slot + 84, 6)
    lv, hp, mx = b[0], struct.unpack('<H', b[2:4])[0], struct.unpack('<H', b[4:6])[0]
    return lv, hp, mx
Game.hp = _hp

def _battle2(self, log=None):
    """trainer battles: fight with a move that has PP. wild battles: fight while HP >= 50%, otherwise run"""
    trainer = self.u32(self.R['btype']) & 0x8
    n = 0; other = 0
    while not self.in_overworld() and n < 600:
        n += 1
        if n % 40 == 0 and log is not None: log.append(self.snap('battle'))
        if not self.in_battle():
            other += 1
            self.tap('B' if other > 4 else 'A')
            continue
        other = 0
        f = self.u32(self.R['bcf'])
        if f == self.R['act']:
            lv, hp, mx = self.hp()
            if not trainer and mx and hp * 2 < mx:
                self.tap('D'); self.tap('R'); self.tap('A')
            else:
                self.tap('U'); self.tap('L'); self.tap('A')
        elif f == self.R['mv']:
            b = self.peek(self.R['bmons'] + 0x0C, 0x1C)
            moves = struct.unpack('<4H', b[0:8]); pp = b[0x18:0x1C]
            t1, t2 = self.peek(self.R['bmons'] + 0x21, 2)
            def score(i):
                if not moves[i] or not pp[i]: return -1
                o = self.R['moves'] - 0x08000000 + 12 * moves[i]
                pw, ty = self.romdata[o + 1], self.romdata[o + 2]
                return pw * (1.5 if ty in (t1, t2) else 1) + 0.01 * (4 - i)
            pick = max(range(4), key=score)
            self.tap('U'); self.tap('L')
            if pick in (1, 3): self.tap('R')
            if pick in (2, 3): self.tap('D')
            self.tap('A')
        elif f == self.R['tgt']:
            self.tap('A')
        else:
            self.tap('A')
    for i in range(30):
        if self.idle(): break
        self.tap('B')
    return self.u8(self.R['outcome'])
Game.battle = _battle2

def _heal_center(self, rec=None):
    """inside a Pokemon Center 1F: talk to the nurse and accept healing"""
    ev = self.events()
    nurse = [o for o in ev['objs'] if o['gfx'] in (52, 0x34)]  # nurse
    if not nurse:
        nurse = sorted(ev['objs'], key=lambda o: o['y'])[:1]
    n = nurse[0]
    self.travel(n['x'], n['y'] + 2)
    self.face('U'); self.tap('A'); self.run(20)
    shots = [self.snap()]
    for i in range(25):
        self.tap('A'); self.run(10)
        if i in (3, 8): shots.append(self.snap())
        if self.idle(): break
    self.mash()
    if rec is not None: rec.append((f'heal {self.pos()}', shots))
Game.heal_center = _heal_center

import re as _re
_MAPS = {}
for _l in open('/home/claude/pret/include/constants/map_groups.h'):
    _m = _re.match(r'#define (MAP_\w+)\s+\((\d+) \| \((\d+) << 8\)\)', _l)
    if _m: _MAPS[_m.group(1)[4:]] = (int(_m.group(3)), int(_m.group(2)))
def mapid(name): return _MAPS[name]

def _enter(self, name, rec=None):
    g_, n_ = mapid(name)
    for t in range(3):
        if not self.idle(): self.handle(rec)
        p = self.warp_to(grp=g_, num=n_)
        if self.pos()[2:] == (g_, n_): break
    if rec is not None: rec.append((f'enter {name}', [self.snap()]))
    return self.pos()[2:] == (g_, n_)
Game.enter = _enter

def _leave(self, name, rec=None):
    """leave a building back to the outdoor map `name`"""
    return self.enter(name, rec)
Game.leave = _leave

def _heal_if_low(self, center, town, back_edge, rec=None, ratio=0.5):
    """if the lead is below ratio, walk (edge back_edge) to `town`, heal at `center`, return"""
    lv, hp, mx = self.hp()
    if mx and hp >= mx * ratio: return False
    here = self.pos()[2:]
    for i in range(4):
        if self.pos()[2:] == mapid(town): break
        self.edge(back_edge, rec)
    self.enter(center, rec); self.heal_center(rec); self.leave(town, rec)
    return True
Game.heal_if_low = _heal_if_low

def compact(recs_en, recs_jp, out, scale=0.5):
    """one shot per side per interaction (the one with text if any), skipping battles"""
    from PIL import Image, ImageDraw
    ee = {l: s for l, s in recs_en}; je = {l: s for l, s in recs_jp}
    order = []
    for l, _ in recs_en + recs_jp:
        if l not in order and 'battle' not in l: order.append(l)
    def pick(sh): return sh[1] if len(sh) > 1 else (sh[0] if sh else None)
    cols = 2; w = int(240 * scale); h = int(160 * scale)
    im = Image.new('RGB', ((w * 2 + 6) * cols, ((len(order) + cols - 1) // cols) * (h + 10)), (30, 30, 30)); d = ImageDraw.Draw(im)
    for i, l in enumerate(order):
        x = (i % cols) * (w * 2 + 6); y = (i // cols) * (h + 10)
        d.text((x, y), l[:40], fill=(255, 255, 0))
        for j, sh in enumerate((ee.get(l, []), je.get(l, []))):
            f = pick(sh)
            if f:
                try: im.paste(Image.open(f).resize((w, h)), (x + j * w, y + 10))
                except Exception: pass
    im.save(out); return out

# ---------------- world graph / navigation between maps
_MAPNAME = {v: k for k, v in _MAPS.items()}
MAPGROUPS = {'jp': 0x08311F50, 'en': 0x083547B0, 'fp': 0x083A716C}
def _hdr(self, g, n):
    r = self.romdata
    def u32r(a): return struct.unpack_from('<I', r, a - 0x08000000)[0]
    try:
        return u32r(u32r(MAPGROUPS[self.k] + 4 * g) + 4 * n)
    except Exception:
        return None
Game.hdr = _hdr

def _edges_of(self, g, n):
    r = self.romdata
    def u32r(a): return struct.unpack_from('<I', r, a - 0x08000000)[0]
    h = self.hdr(g, n); out = []
    if not h: return out
    con = u32r(h + 12)
    if con:
        cnt, ptr = struct.unpack_from('<iI', r, con - 0x08000000)
        for i in range(min(cnt, 8)):
            d, off, mg, mn = struct.unpack_from('<BxxxiBB', r, ptr - 0x08000000 + 12 * i)
            dl = {1: 'D', 2: 'U', 3: 'L', 4: 'R'}.get(d)
            if dl: out.append(('edge', dl, (mg, mn)))
    ev = u32r(h + 4)
    nw = r[ev - 0x08000000 + 1]; pw = u32r(ev + 8)
    seen = set()
    for i in range(nw):
        x, y, el, wid, mn, mg = struct.unpack_from('<hhBBBB', r, pw - 0x08000000 + 8 * i)
        if mg == 0x7F or (mg, mn) in seen: continue
        seen.add((mg, mn)); out.append(('warp', None, (mg, mn)))
    return out
Game.edges_of = _edges_of

def _route(self, goal_fn, start=None):
    start = start or self.pos()[2:]
    blocked = getattr(self, 'blocked', set())
    prev = {start: None}; q = collections.deque([start])
    while q:
        cur = q.popleft()
        if goal_fn(cur) and cur != start: break
        for kind, d, nxt in self.edges_of(*cur):
            if nxt in prev or (cur, nxt) in blocked: continue
            prev[nxt] = (cur, kind, d); q.append(nxt)
    else:
        return None
    hops = []; c = cur
    while prev[c]: p, kind, d = prev[c]; hops.append((p, kind, d, c)); c = p
    return hops[::-1]
Game.route = _route

def _nav(self, target, rec=None, max_hops=40):
    """walk to map `target` (name or (g,n)) using map connections and warps"""
    tgt = mapid(target) if isinstance(target, str) else target
    if not hasattr(self, 'blocked'): self.blocked = set()
    for attempt in range(max_hops):
        if not self.idle(): self.handle(rec)
        cur = self.pos()[2:]
        if cur == tgt: return True
        if self.low() and not _MAPNAME.get(cur, '').endswith('POKEMON_CENTER_1F'):
            self.heal_nearest(rec); continue
        hops = self.route(lambda m: m == tgt)
        if not hops: return False
        p, kind, d, nxt = hops[0]
        if kind == 'edge': self.edge(d, rec)
        else: self.warp_to(grp=nxt[0], num=nxt[1])
        if not self.idle(): self.handle(rec)
        if self.pos()[2:] == cur:
            self.blocked.add((cur, nxt))
    return self.pos()[2:] == tgt
Game.nav = _nav

def _heal_nearest(self, rec=None):
    if getattr(self, '_healing', False): return False
    self._healing = True
    try: return self._heal_nearest2(rec)
    finally: self._healing = False
def _heal_nearest2(self, rec=None):
    here = self.pos()[2:]
    hops = self.route(lambda m: _MAPNAME.get(m, '').endswith('POKEMON_CENTER_1F'))
    if hops is None: return False
    pc = hops[-1][3]
    self.nav(pc, rec)
    if self.pos()[2:] == pc: self.heal_center(rec)
    self.nav(here, rec)
    return True
Game.heal_nearest = _heal_nearest
Game._heal_nearest2 = _heal_nearest2

def _hop(self, nxt, rec=None, tries=3):
    tgt = mapid(nxt) if isinstance(nxt, str) else nxt
    for t in range(tries):
        if not self.idle(): self.handle(rec)
        cur = self.pos()[2:]
        if cur == tgt: return True
        if self.low() and not _MAPNAME.get(cur, '').endswith('POKEMON_CENTER_1F'):
            self.heal_nearest(rec)
        es = [e for e in self.edges_of(*cur) if e[2] == tgt]
        if not es: return False
        kind, d, _ = es[0]
        if kind == 'edge': self.edge(d, rec)
        else: self.warp_to(grp=tgt[0], num=tgt[1])
        if not self.idle(): self.handle(rec)
    return self.pos()[2:] == tgt
Game.hop = _hop

def _go(self, maps, rec=None):
    self.trail = getattr(self, 'trail', [])
    for m in maps:
        here = self.pos()[2:]
        if not self.hop(m, rec): return False
        self.trail.append(here)
        self.trail = self.trail[-30:]
    return True
Game.go = _go

def _heal_nearest2(self, rec=None):
    """walk back along the trail of visited maps to the most recent Pokemon Center, heal, and come back"""
    here = self.pos()[2:]
    trail = list(getattr(self, 'trail', []))
    path = []
    for m in reversed(trail):
        path.append(m)
        if _MAPNAME.get(m, '').endswith('POKEMON_CENTER_1F'): break
        # a town with a center: enter it from the town
        name = _MAPNAME.get(m, '')
        pc = mapid(name + '_POKEMON_CENTER_1F') if (name + '_POKEMON_CENTER_1F') in _MAPS else None
        if pc: path.append(pc); break
    else:
        return False
    back = [here]
    for m in path:
        cur = self.pos()[2:]
        if not self.hop(m, rec): return False
        back.append(cur)
    self.heal_center(rec)
    for m in reversed(back[1:-1] + [here]) if False else list(reversed(back))[1:]:
        pass
    # walk the same maps back
    for m in reversed(back[:-1] + [path[-2]] if len(path) > 1 else back[:-1]):
        pass
    rev = list(reversed([here] + path[:-1]))
    for m in rev:
        if not self.hop(m, rec): break
    return True
Game._heal_nearest2 = _heal_nearest2

def _party(self):
    ORD = ['GAEM','GAME','GEAM','GEMA','GMAE','GMEA','AGEM','AGME','AEGM','AEMG','AMGE','AMEG','EGAM','EGMA','EAGM','EAMG','EMGA','EMAG','MGAE','MGEA','MAGE','MAEG','MEGA','MEAG']
    out = []
    for s in range(self.u8(self.R['cnt'])):
        b = self.peek(self.R['party'] + 100 * s, 100)
        pid, ot = struct.unpack_from('<II', b, 0); key = pid ^ ot
        dec = b''.join(struct.pack('<I', struct.unpack_from('<I', b, 32 + i)[0] ^ key) for i in range(0, 48, 4))
        o = ORD[pid % 24]; G = dec[o.index('G') * 12:][:12]; A = dec[o.index('A') * 12:][:12]
        sp = struct.unpack_from('<H', G)[0]; mv = struct.unpack_from('<4H', A); pp = A[8:12]
        out.append(dict(species=sp, level=b[84], hp=struct.unpack_from('<H', b, 86)[0], maxhp=struct.unpack_from('<H', b, 88)[0], moves=mv, pp=tuple(pp)))
    return out
Game.party = _party

def _dungeon(self, target, rec=None, explore=True, max_moves=40, exclude=()):
    """depth-first through a multi-map dungeon using only warps the player can actually reach"""
    tgt = mapid(target) if isinstance(target, str) else target
    used = set((mapid(m) if isinstance(m, str) else m, i) for m, i in exclude); fixed = set(used); seen_maps = set()
    for step in range(max_moves):
        if not self.idle(): self.handle(rec)
        cur = self.pos()[2:]
        if cur == tgt: return True
        if explore and cur not in seen_maps:
            seen_maps.add(cur); self.explore(rec)
        ws = self.events()['warps']
        cands = []
        for i, w in enumerate(ws):
            dest = (w['grp'], w['num'])
            if (cur, i) in used: continue
            p = self.path(w['x'], w['y'])
            if p is None and self.pos()[:2] != (w['x'], w['y']): continue
            pri = 0 if dest == tgt else (1 if dest not in seen_maps else 2)
            cands.append((pri, i, dest))
        if not cands:
            used = {u for u in used if u[0] != cur or u in fixed}   # allow re-use
            continue
        cands.sort()
        pri, i, dest = cands[0]
        used.add((cur, i))
        self.warp_to(idx=i)
        if not self.idle(): self.handle(rec)
    return self.pos()[2:] == tgt
Game.dungeon = _dungeon


def _teleport(self, name, x, y):
    """warp anywhere: a one-command script in gStringVar4 run by the global script context"""
    grp, num = mapid(name); buf = self.R['strbuf'] + 0x200
    data = bytes([0x39, grp, num, 0xFF]) + struct.pack('<hh', x, y) + b'\x02'
    for i, b in enumerate(data): self.cmd(f'poke {buf + i:08X} {b:02X}')
    for a, v in ((0x03000EB1, b'\x01'), (0x03000EB0, b'\x00'), (0x03000EB8, struct.pack('<I', buf)), (0x03000EA8, b'\x00')):
        for i, b in enumerate(v): self.cmd(f'poke {a + i:08X} {b:02X}')
    for i in range(40):
        self.run(20)
        if self.pos()[2:] == (grp, num) and self.idle(): break
    self.run(60)
    return self.pos()
Game.teleport = _teleport
def _setflag(self, f, on=True):
    a = self.sb1() + 0xEE0 + f // 8; v = self.u8(a)
    self.cmd(f'poke {a:08X} {((v | (1 << (f % 8))) if on else (v & ~(1 << (f % 8)))) & 0xFF:02X}')
Game.setflag = _setflag
def _getflag(self, f): return (self.u8(self.sb1() + 0xEE0 + f // 8) >> (f % 8)) & 1
Game.getflag = _getflag
def _setvar(self, v, val):
    a = self.sb1() + 0x1000 + 2 * (v - 0x4000)
    for i, b in enumerate(struct.pack('<H', val)): self.cmd(f'poke {a + i:08X} {b:02X}')
Game.setvar = _setvar
def _getvar(self, v): return self.u16(self.sb1() + 0x1000 + 2 * (v - 0x4000))
Game.getvar = _getvar
