#!/usr/bin/env python3
# Extracts the Battle Tower BGM (song 384) from Japanese Pokémon Ruby, with its voicegroup, keysplit tables and samples,
# into a relocatable blob: port/sound/rs_btower/song.bin + song.json (pointer fixups, header offset).
# patch_port.py (via bt_patch.py) copies the blob into the JP FireRed ROM and adds it to the song table.
import struct, json, os, sys
RUBY = '/home/claude/roms/Pocket Monsters - Ruby (Japan).gba'
SONG_TABLE = 0x416EE4
SONG = 384
OUT = '/home/claude/port/sound/rs_btower'
r = open(RUBY, 'rb').read()
assert r[0xA0:0xAC] == b'POKEMON RUBY'
def u32(o): return struct.unpack_from('<I', r, o)[0]
def isptr(v): return 0x08000000 <= v < 0x08000000 + len(r)

blob = bytearray(); fix = []          # fix: blob offsets holding blob-relative offsets
placed = {}                           # (kind, rom addr) -> blob offset
def put(data, align=4):
    while len(blob) % align: blob.append(0)
    o = len(blob); blob.extend(data); return o
def setptr(at, off):
    struct.pack_into('<I', blob, at, off); fix.append(at)

hdr = u32(SONG_TABLE + 8 * SONG) - 0x08000000
tc = r[hdr]
tracks = [u32(hdr + 8 + 4 * i) - 0x08000000 for i in range(tc)]
vg = u32(hdr + 4) - 0x08000000
lo, hi = min(tracks), hdr                         # all track data sits right before the header
# track data: copy as one block, relocate GOTO/PATT/REPT pointers that point inside it
tblk = put(r[lo:hi], 1)
used_voices = set()
for t in tracks:
    i = t
    end = hi if t == max(tracks) else min(x for x in tracks if x > t)
    while i < end:
        b = r[i]
        if b in (0xB2, 0xB3) and i + 5 <= hi and lo <= u32(i + 1) - 0x08000000 < hi:
            setptr(tblk + i + 1 - lo, tblk + u32(i + 1) - 0x08000000 - lo); i += 5; continue
        if b == 0xB5 and lo <= u32(i + 2) - 0x08000000 < hi:
            setptr(tblk + i + 2 - lo, tblk + u32(i + 2) - 0x08000000 - lo); i += 6; continue
        if b == 0xBD and r[i + 1] < 0x80:
            used_voices.add(r[i + 1])
        i += 1
print('tracks', tc, 'track bytes', hi - lo, 'voices', sorted(used_voices))

def wave(addr):
    k = ('ds', addr)
    if k not in placed:
        size = u32(addr - 0x08000000 + 12)
        placed[k] = put(r[addr - 0x08000000: addr - 0x08000000 + 16 + size + 1])
    return placed[k]
def pwave(addr):
    k = ('pw', addr)
    if k not in placed: placed[k] = put(r[addr - 0x08000000: addr - 0x08000000 + 16])
    return placed[k]
def ksplit(addr):
    k = ('ks', addr)
    if k not in placed: placed[k] = put(r[addr - 0x08000000: addr - 0x08000000 + 128], 1)
    return placed[k]

SILENT = bytes([1, 60, 0, 0, 0, 0, 0, 0, 0, 0, 15, 0])   # square 1, envelope 0
def voicegroup(addr, which, depth=0):
    """copy entries `which` of the voicegroup at addr; other entries become silent. Returns blob offset."""
    key = ('vg', addr, tuple(which))
    if key in placed: return placed[key]
    n = max(which) + 1
    o = put(b''.join(SILENT for _ in range(n)))
    placed[key] = o
    for v in which:
        e = addr - 0x08000000 + 12 * v
        ent = bytearray(r[e:e + 12]); typ = ent[0]
        if depth and typ in (0x40, 0x80):                     # entries past the end of a drum kit: leave silent
            continue
        blob[o + 12 * v: o + 12 * v + 12] = ent
        if typ in (0x00, 0x08, 0x10, 0x18):                  # direct sound
            setptr(o + 12 * v + 4, wave(struct.unpack_from('<I', ent, 4)[0]))
        elif typ in (0x03, 0x0B):                             # programmable wave
            setptr(o + 12 * v + 4, pwave(struct.unpack_from('<I', ent, 4)[0]))
        elif typ == 0x40:                                     # keysplit
            sub, ks = struct.unpack_from('<II', ent, 4)
            kso = ksplit(ks)
            subs = sorted(set(blob[kso:kso + 128]))
            setptr(o + 12 * v + 4, voicegroup(sub, subs, depth + 1)); setptr(o + 12 * v + 8, kso)
        elif typ == 0x80:                                     # drum kit (keysplit all)
            sub = struct.unpack_from('<I', ent, 4)[0]
            setptr(o + 12 * v + 4, voicegroup(sub, range(128), depth + 1))
        elif typ & 7 in (1, 2, 4):                            # square / noise: no pointers
            pass
        else:
            raise SystemExit(f'unknown voice type {typ:#x} at {addr + 12 * v:#x}')
    return o

vgo = voicegroup(vg + 0x08000000, sorted(used_voices))
# header
h = bytearray(r[hdr:hdr + 8 + 4 * tc])
ho = put(h)
setptr(ho + 4, vgo)
for i, t in enumerate(tracks): setptr(ho + 8 + 4 * i, tblk + t - lo)
os.makedirs(OUT, exist_ok=True)
open(OUT + '/song.bin', 'wb').write(blob)
json.dump({'header': ho, 'fixups': fix, 'ms': struct.unpack_from('<HH', r, SONG_TABLE + 8 * SONG + 4)}, open(OUT + '/song.json', 'w'))
print('blob', len(blob), 'fixups', len(fix), 'samples', sum(1 for k in placed if k[0] == 'ds'))
