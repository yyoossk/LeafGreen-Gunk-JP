# FRLG+ RS Battle Tower assets -> port/data/hooks/btts/ (tilesets, anim frames, layouts, object sprites)
import subprocess, os, shutil, json
F = '/home/claude/frlgplus/'
O = '/home/claude/port/data/hooks/btts/'
GBAGFX = '/home/claude/pret/tools/gbagfx/gbagfx'
def g(*a): subprocess.check_call([GBAGFX] + list(a))
os.makedirs(O, exist_ok=True)
for name, d in [('bf', 'battlefrontier'), ('bfe', 'battlefrontieroutsideeast')]:
    src = F + 'data/tilesets/secondary/%s/' % d
    g(src + 'tiles.png', O + name + '_tiles.4bpp')
    g(O + name + '_tiles.4bpp', O + name + '_tiles.4bpp.lz')
    pals = b''
    for k in range(16):
        p = src + 'palettes/%02d.pal' % k
        if os.path.exists(p):
            g(p, O + name + '_pal.gbapal'); pals += open(O + name + '_pal.gbapal', 'rb').read()
        else:
            pals += b'\0' * 32
    os.remove(O + name + '_pal.gbapal')
    open(O + name + '_pals.bin', 'wb').write(pals)
    shutil.copy(src + 'metatiles.bin', O + name + '_metatiles.bin')
    shutil.copy(src + 'metatile_attributes.bin', O + name + '_attrs.bin')
for kind, n in [('flag', 4), ('flower', 3)]:
    for k in range(n):
        g(F + 'data/tilesets/secondary/battlefrontieroutsideeast/anim/%s/%d.png' % (kind, k), O + 'bfe_%s%d.4bpp' % (kind, k))
L = {l['id']: l for l in json.load(open(F + 'data/layouts/layouts.json'))['layouts'] if 'id' in l}
for lid, short in [('LAYOUT_RS_BATTLE_TOWER', 'out'), ('LAYOUT_RS_BATTLE_TOWER_LOBBY', 'lobby'), ('LAYOUT_RS_BATTLE_TOWER_ELEVATOR', 'elev'),
                   ('LAYOUT_RS_BATTLE_TOWER_CORRIDOR', 'corr'), ('LAYOUT_RS_BATTLE_TOWER_BATTLE_ROOM', 'room')]:
    shutil.copy(F + L[lid]['blockdata_filepath'], O + 'lay_%s_map.bin' % short)
    shutil.copy(F + L[lid]['border_filepath'], O + 'lay_%s_border.bin' % short)
g(F + 'graphics/object_events/pics/people/scott.png', O + 'ow_scott.4bpp', '-mwidth', '2', '-mheight', '4')
g(F + 'graphics/object_events/pics/pokemon/sudowoodo.png', O + 'ow_sudowoodo.4bpp', '-mwidth', '2', '-mheight', '4')
for f in sorted(os.listdir(O)): print(f, os.path.getsize(O + f))
