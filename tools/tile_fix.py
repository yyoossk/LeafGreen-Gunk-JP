# exec'd from patch_port.py: FRLG+ vanilla tile-error fixes.
# Merges FRLG+'s changes (relative to pret) into the JP tilesets tile-by-tile / colour-by-colour / metatile-by-metatile,
# so JP-only graphics (Japanese signs etc.) are kept, then applies FRLG+'s small layout fixes where the JP map matches pret.
# FRLG+'s redesigns (Sevii Islands, Berry Forest, Safari Zone, Victory Road, caves) are not taken: they renumber tilesets
# and resize maps, which is a remodel rather than a fix.
import json as _j
from PIL import Image as _Im
_P = '/home/claude/pret'; _F = '/home/claude/frlgplus'

def _lz_dec(a):
    s = a - 0x08000000; assert rom[s] == 0x10
    n = rom[s + 1] | rom[s + 2] << 8 | rom[s + 3] << 16; o = bytearray(); i = s + 4
    while len(o) < n:
        f = rom[i]; i += 1
        for b in range(8):
            if len(o) >= n: break
            if f & (0x80 >> b):
                x = rom[i] << 8 | rom[i + 1]; i += 2
                l = (x >> 12) + 3; d = (x & 0xFFF) + 1
                for _ in range(l): o.append(o[-d])
            else:
                o.append(rom[i]); i += 1
    return bytes(o)

def _lz_enc(d):
    out = bytearray([0x10, len(d) & 0xFF, len(d) >> 8 & 0xFF, len(d) >> 16 & 0xFF]); i = 0
    while i < len(d):
        fp = len(out); out.append(0); flags = 0
        for b in range(8):
            if i >= len(d): break
            best_l = 0; best_d = 0
            for dist in range(2, min(i, 4096) + 1):          # dist >= 2: safe for VRAM
                l = 0
                while l < 18 and i + l < len(d) and d[i + l] == d[i + l - dist]: l += 1
                if l > best_l: best_l, best_d = l, dist
                if l == 18: break
            if best_l >= 3:
                flags |= 0x80 >> b; x = (best_l - 3) << 12 | (best_d - 1); out += bytes([x >> 8, x & 0xFF]); i += best_l
            else:
                out.append(d[i]); i += 1
        out[fp] = flags
    while len(out) % 4: out.append(0)
    return bytes(out)

def _png_tiles(path):
    im = _Im.open(path); px = im.load(); w = im.width // 8; t = []
    for k in range(w * (im.height // 8)):
        tx, ty = k % w, k // w; b = bytearray()
        for y in range(8):
            for x in range(0, 8, 2):
                b.append((px[tx * 8 + x, ty * 8 + y] & 15) | (px[tx * 8 + x + 1, ty * 8 + y] & 15) << 4)
        t.append(bytes(b))
    return t

def _pal(path):
    L = [l for l in open(path).read().split('\n')[3:19] if l.strip()]
    return [((int(r) >> 3) | (int(g) >> 3) << 5 | (int(b) >> 3) << 10) for r, g, b in (l.split() for l in L)]

_TS = {  # JP tileset symbol -> decomp dir
    'General': 'primary/general', 'Building': 'primary/building', 'CeladonCity': 'secondary/celadon_city',
    'CeruleanCave': 'secondary/cerulean_cave', 'CeruleanCity': 'secondary/cerulean_city', 'CinnabarIsland': 'secondary/cinnabar_island',
    'HoennBuilding': 'secondary/hoenn_building', 'Museum': 'secondary/museum', 'PewterCity': 'secondary/pewter_city',
    'PokemonCenter': 'secondary/pokemon_center', 'ViridianCity': 'secondary/viridian_city', 'SSAnne': 'secondary/ss_anne',
    'SilphCo': 'secondary/silph_co', 'SeafoamIslands': 'secondary/seafoam_islands', 'SafariZoneBuilding': 'secondary/safari_zone_building',
    'LavenderTown': 'secondary/lavender_town', 'IslandHarbor': 'secondary/island_harbor',
}
_hdrs = open(_P + '/src/data/tilesets/headers.h').read(); _gfxc = open(_P + '/src/graphics.c').read() + open(_P + '/src/data/tilesets/graphics.h').read(); _mth = open(_P + '/src/data/tilesets/metatiles.h').read()
def _dirs(n):
    m = re.search(r'const struct Tileset gTileset_' + n + r' =\s*\{(.*?)\};', _hdrs, re.S).group(1)
    t = re.search(r'\.tiles = (\w+)', m).group(1); mt = re.search(r'\.metatiles = (\w+)', m).group(1)
    g = re.search(t + r'\[\] = INCBIN_U32\("data/tilesets/([^"]+)/tiles', _gfxc).group(1)
    md = re.search(mt + r'\[\] = INCBIN_U16\("data/tilesets/([^"]+)/metatiles', _mth).group(1)
    return g, md
_newcount = {}
_tsaddr = {}
_TS['Condominiums'] = ''
for _n in _TS:
    _g, _d = _dirs(_n)
    _ta = jp('gTileset_' + _n)[1]; _tsaddr[_n] = _ta
    _comp, _sec = rom[_ta - 0x08000000], rom[_ta - 0x08000000 + 1]
    _tp, _pp, _mp, _cb, _ap = struct.unpack_from('<IIIII', rom, _ta - 0x08000000 + 4)
    _pt = _png_tiles(f'{_P}/data/tilesets/{_g}/tiles.png'); _ft = _png_tiles(f'{_F}/data/tilesets/{_g}/tiles.png')
    # tiles
    _jt = _lz_dec(_tp) if _comp else bytes(rom[_tp - 0x08000000: _tp - 0x08000000 + 32 * len(_pt)])
    _jt = [_jt[32 * k: 32 * k + 32] for k in range(len(_jt) // 32)]
    _ch = [k for k in range(len(_ft)) if k >= len(_pt) or _ft[k] != _pt[k]]
    _jpdiff = [k for k in _ch if k < len(_pt) and k < len(_jt) and _jt[k] != _pt[k]]
    _nt = list(_jt) + [bytes(32)] * max(0, len(_ft) - len(_jt))
    for k in _ch:
        if k in _jpdiff: continue                     # JP-specific graphics: keep
        _nt[k] = _ft[k]
    while len(_nt) > len(_jt) and _nt[-1] == bytes(32) and len(_nt) > len(_ft): _nt.pop()
    if _ch and _ch != _jpdiff:
        _raw = b''.join(_nt)
        _new = alloc(_lz_enc(_raw)) if _comp else alloc(_raw)
        struct.pack_into('<I', rom, _ta - 0x08000000 + 4, _new)
    # palettes (16 x 16 colours)
    _np = bytearray(rom[_pp - 0x08000000: _pp - 0x08000000 + 512]); _pc = 0
    for _i in range(16):
        _a = f'{_P}/data/tilesets/{_g}/palettes/{_i:02d}.pal'; _b = f'{_F}/data/tilesets/{_g}/palettes/{_i:02d}.pal'
        if not (os.path.exists(_a) and os.path.exists(_b)): continue
        for _c, (_x, _y) in enumerate(zip(_pal(_a), _pal(_b))):
            if _x != _y: struct.pack_into('<H', _np, 32 * _i + 2 * _c, _y); _pc += 1
    if _pc: struct.pack_into('<I', rom, _ta - 0x08000000 + 8, alloc(bytes(_np)))
    # metatiles + attributes
    _pm = open(f'{_P}/data/tilesets/{_d}/metatiles.bin', 'rb').read(); _fm = open(f'{_F}/data/tilesets/{_d}/metatiles.bin', 'rb').read()
    _pa = open(f'{_P}/data/tilesets/{_d}/metatile_attributes.bin', 'rb').read(); _fa = open(f'{_F}/data/tilesets/{_d}/metatile_attributes.bin', 'rb').read()
    _jm = bytearray(rom[_mp - 0x08000000: _mp - 0x08000000 + len(_pm)]); _ja = bytearray(rom[_ap - 0x08000000: _ap - 0x08000000 + len(_pa)])
    _mc = 0
    for k in range(len(_fm) // 16):
        if k < len(_pm) // 16 and _fm[16 * k:16 * k + 16] == _pm[16 * k:16 * k + 16]: continue
        if k < len(_pm) // 16 and _jm[16 * k:16 * k + 16] != _pm[16 * k:16 * k + 16]: continue
        if k >= len(_jm) // 16: _jm += bytes(16 * (k + 1 - len(_jm) // 16))
        _jm[16 * k:16 * k + 16] = _fm[16 * k:16 * k + 16]; _mc += 1
    for k in range(len(_fa) // 4):
        if k < len(_pa) // 4 and _fa[4 * k:4 * k + 4] == _pa[4 * k:4 * k + 4]: continue
        if k < len(_pa) // 4 and _ja[4 * k:4 * k + 4] != _pa[4 * k:4 * k + 4] and _n != 'SeafoamIslands': continue
        if k >= len(_ja) // 4: _ja += bytes(4 * (k + 1 - len(_ja) // 4))
        _ja[4 * k:4 * k + 4] = _fa[4 * k:4 * k + 4]; _mc += 1
    if _mc:
        struct.pack_into('<I', rom, _ta - 0x08000000 + 12, alloc(bytes(_jm)))
        struct.pack_into('<I', rom, _ta - 0x08000000 + 20, alloc(bytes(_ja)))
    _newcount[_n] = len(_jm) // 16
    print('tilefix', _n, 'tiles', len(_ch), '(jp-kept', len(_jpdiff), ') cols', _pc, 'metatiles/attrs', _mc)

# layouts: small FRLG+ fixes on maps that keep their size
_SKIP_MAPS = {'SevenIsland_House_Room2', 'RS_BattleTower',          # FRLG+ furniture for its own feature, not a fix
              'SSAnne_Room1'}   # FRLG+'s desk/plant metatiles (0x3C8-) show garbage on the JP tiles (S.S. Anne 1F rooms)
# FRLG+ also moves the Viridian / Celadon / Cinnabar gym buildings by one tile and moves the door warps with them;
# only the blocks would come over here, leaving the door warp on a wall, so those gym blocks are kept as they are.
_SKIP_MAPS |= {'CeladonCity', 'CinnabarIsland'}
_SKIP_CELLS = {'ViridianCity': lambda x, y: x >= 30 and y <= 11}
_alll = _j.load(open(_P + '/data/layouts/layouts.json'))['layouts']
_lay = {l['blockdata_filepath'].split('/')[2]: l for l in _alll if 'blockdata_filepath' in l}
_lidx = {l['blockdata_filepath'].split('/')[2]: i for i, l in enumerate(_alll) if 'blockdata_filepath' in l}
_LT = u32at(0x08054A30)
_tsym = {('gTileset_' + k): k for k in _TS}
for _name, _L in sorted(_lay.items()):
    if _name in _SKIP_MAPS: continue
    _ok = True
    for _ts in (_L['primary_tileset'], _L['secondary_tileset']):
        if _ts in _tsym: continue
        try: _g2, _d2 = _dirs(_ts[len('gTileset_'):])
        except Exception: _ok = False; break
        if all(open(f'{_P}/data/tilesets/{x}', 'rb').read() == open(f'{_F}/data/tilesets/{x}', 'rb').read() for x in (_d2 + '/metatiles.bin', _d2 + '/metatile_attributes.bin')):
            _tsym[_ts] = _ts[len('gTileset_'):]; _newcount[_tsym[_ts]] = len(open(f'{_P}/data/tilesets/{_d2}/metatiles.bin', 'rb').read()) // 16
        else: _ok = False
    if not _ok: continue
    for _fn in ('map.bin', 'border.bin'):
        _pf = f"{_P}/data/layouts/{_name}/{_fn}"; _ff = f"{_F}/data/layouts/{_name}/{_fn}"
        if not os.path.exists(_ff): continue
        _a = open(_pf, 'rb').read(); _b = open(_ff, 'rb').read()
        if _a == _b or len(_a) != len(_b): continue
        _cells = [k for k in range(len(_a) // 2) if _a[2 * k:2 * k + 2] != _b[2 * k:2 * k + 2]]
        if len(_cells) > 60: print('tilefix skip (remodel)', _name, _fn, len(_cells)); continue
        _sec = _newcount[_tsym[_L['secondary_tileset']]]
        if any((struct.unpack_from('<H', _b, 2 * k)[0] & 0x3FF) >= 640 + _sec for k in _cells):
            print('tilefix skip (metatile out of range)', _name); continue
        _lp = u32at(_LT + 4 * _lidx[_name])
        _at = u32at(_lp + (12 if _fn == 'map.bin' else 8)) - 0x08000000
        if bytes(rom[_at:_at + len(_a)]) != _a: print('tilefix skip (JP map differs)', _name, _fn); continue
        if _name in _SKIP_CELLS and _fn == 'map.bin':
            _cells = [k for k in _cells if not _SKIP_CELLS[_name](k % _L['width'], k // _L['width'])]
        for k in _cells: rom[_at + 2 * k: _at + 2 * k + 2] = _b[2 * k:2 * k + 2]
        print('tilefix map', _name, _fn, len(_cells))
