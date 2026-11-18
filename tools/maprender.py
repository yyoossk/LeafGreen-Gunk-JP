#!/usr/bin/env python3
# Render a pret-style layout (map.bin + tilesets from a decomp tree) to PNG. Used to inspect FRLG+ tile fixes.
import json, re, struct, os, sys
from PIL import Image

def tileset_dir(root, sym):
    hdr = open(f'{root}/src/data/tilesets/headers.h').read()
    m = re.search(r'const struct Tileset ' + sym + r' =\s*\{(.*?)\};', hdr, re.S)
    tiles = re.search(r'\.tiles = (\w+)', m.group(1)).group(1)
    g = open(f'{root}/src/graphics.c').read() + (open(f'{root}/src/data/tilesets/graphics.h').read() if os.path.exists(f'{root}/src/data/tilesets/graphics.h') else '')
    p = re.search(tiles + r'\[\] = INCBIN_U32\("([^"]+)"', g).group(1)
    return os.path.dirname(f'{root}/{p}')

def load_ts(root, sym):
    d = tileset_dir(root, sym)
    img = Image.open(d + '/tiles.png')
    pal = []
    for i in range(16):
        f = f'{d}/palettes/{i:02d}.pal'
        if os.path.exists(f):
            L = open(f).read().split('\n')[3:19]
            pal.append([tuple((int(x)>>3)<<3 for x in l.split()) for l in L if l.strip()])
        else:
            pal.append([(0, 0, 0)] * 16)
    mt = open(d + '/metatiles.bin', 'rb').read()
    w = img.width // 8
    px = img.load()
    tiles = []
    for t in range((img.width // 8) * (img.height // 8)):
        tx, ty = t % w, t // w
        tiles.append([[px[tx * 8 + x, ty * 8 + y] & 15 for x in range(8)] for y in range(8)])
    return tiles, pal, mt

def render(root, layout_id, mapbin=None, scale=1):
    d = json.load(open(f'{root}/data/layouts/layouts.json'))
    L = [l for l in d['layouts'] if l.get('id') == layout_id][0]
    pt, pp, pm = load_ts(root, L['primary_tileset'])
    st, sp, sm = load_ts(root, L['secondary_tileset'])
    tiles = pt[:640] + [[[0] * 8] * 8] * max(0, 640 - len(pt)) + st
    pal = pp[:7] + sp[7:]
    blk = open(mapbin or f"{root}/{L['blockdata_filepath']}", 'rb').read()
    W, H = L['width'], len(blk) // 2 // L['width']
    im = Image.new('RGB', (W * 16, H * 16))
    P = im.load()
    for i in range(W * H):
        v = struct.unpack_from('<H', blk, 2 * i)[0] & 0x3FF
        mt = pm if v < 640 else sm
        o = (v if v < 640 else v - 640) * 16
        if o + 16 > len(mt): continue
        for layer in range(2):
            for q in range(4):
                e = struct.unpack_from('<H', mt, o + layer * 8 + q * 2)[0]
                t, hf, vf, pl = e & 0x3FF, e >> 10 & 1, e >> 11 & 1, e >> 12
                if t >= len(tiles): continue
                tt = tiles[t]
                bx, by = (i % W) * 16 + (q & 1) * 8, (i // W) * 16 + (q >> 1) * 8
                for y in range(8):
                    for x in range(8):
                        c = tt[7 - y if vf else y][7 - x if hf else x]
                        if c == 0 and layer: continue
                        P[bx + x, by + y] = pal[pl][c] if pl < len(pal) and c < len(pal[pl]) else (255, 0, 255)
    return im

if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2]).save(sys.argv[3])
