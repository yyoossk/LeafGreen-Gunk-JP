# exec'd from patch_port.py when V151=1: 151匹揃う版
# A. LeafGreen wild encounter tables (+ trade-only Pokémon added to the wild), used half of the time
import json as _js, re as _re
_P = '/home/claude/pret'
_SP = {}
for _l in open(_P + '/include/constants/species.h'):
    _m = _re.match(r'#define (SPECIES_\w+)\s+(\d+)\s*$', _l)
    if _m: _SP[_m.group(1)] = int(_m.group(2))
_W = _js.load(open(_P + '/src/data/wild_encounters.json'))['wild_encounter_groups'][0]
_FR = [e for e in _W['encounters'] if e['base_label'].endswith('_FireRed')]
_LG = [e for e in _W['encounters'] if e['base_label'].endswith('_LeafGreen')]
_KINDS = ['land_mons', 'water_mons', 'rock_smash_mons', 'fishing_mons']
_OLD = 0x0838C164; _N = 132

# trade-only Pokémon put into the wild (kit 2-3): map -> (species, level); replaces one low-rate land slot
# whose species also appears in another slot of the same table
_ADD = {'MAP_ROUTE12': ('SPECIES_FARFETCHD', 26), 'MAP_ROUTE13': ('SPECIES_FARFETCHD', 26),
        'MAP_SAFARI_ZONE_EAST': ('SPECIES_LICKITUNG', 25), 'MAP_SAFARI_ZONE_WEST': ('SPECIES_LICKITUNG', 25),
        'MAP_SEAFOAM_ISLANDS_B2F': ('SPECIES_JYNX', 30), 'MAP_SEAFOAM_ISLANDS_B4F': ('SPECIES_JYNX', 32),
        'MAP_ROUTE21_NORTH': ('SPECIES_MR_MIME', 25), 'MAP_ROUTE21_SOUTH': ('SPECIES_MR_MIME', 25)}
_ADDED = []
def _pick_slot(sp):
    # prefer the 5% slots, then 4%, then 1%; the replaced species must still appear elsewhere
    for s in (6, 7, 8, 9, 10, 11):
        if sum(1 for x in sp if x == sp[s]) > 1: return s
    return 7

def _apply_add(mapname, mons_get, mons_set, label):
    if mapname not in _ADD: return
    spn, lv = _ADD[mapname]
    sp = [mons_get(i)[2] for i in range(12)]
    s = _pick_slot(sp)
    mons_set(s, lv, lv, _SP[spn])
    _ADDED.append((label, mapname, spn, s, lv))

# FireRed side (in place, in the JP ROM's own tables)
for _i, _e in enumerate(_FR):
    _h = _OLD + 20 * _i
    _land = u32at(_h + 4)
    if _land:
        _arr = u32at(_land + 4)
        def _get(i, a=_arr): return struct.unpack_from('<BBH', rom, a - 0x08000000 + 4 * i)
        def _set(i, mn, mx, sp, a=_arr): struct.pack_into('<BBH', rom, a - 0x08000000 + 4 * i, mn, mx, sp)
        _apply_add(_e['map'], _get, _set, 'FR')

# LeafGreen side (built from the decomp data)
_lg_headers = b''
for _i, _e in enumerate(_LG):
    _g, _n = rom[_OLD - 0x08000000 + 20 * _i], rom[_OLD - 0x08000000 + 20 * _i + 1]
    _ptrs = []
    for _k, _f in zip(_KINDS, _W['fields']):
        if _k not in _e: _ptrs.append(0); continue
        _mons = [[m['min_level'], m['max_level'], _SP[m['species']]] for m in _e[_k]['mons']]
        if _k == 'land_mons':
            def _get(i, M=_mons): return M[i]
            def _set(i, mn, mx, sp, M=_mons): M[i] = [mn, mx, sp]
            _apply_add(_e['map'], _get, _set, 'LG')
        _arr = alloc(b''.join(struct.pack('<BBH', *m) for m in _mons))
        _ptrs.append(alloc(struct.pack('<BxxxI', _e[_k]['encounter_rate'], _arr)))
    _lg_headers += struct.pack('<BBxxIIII', _g, _n, *_ptrs)
_fr_headers = bytes(rom[_OLD - 0x08000000: _OLD - 0x08000000 + 20 * _N])
_term = bytes(rom[_OLD - 0x08000000 + 20 * _N: _OLD - 0x08000000 + 20 * _N + 20])
_NEW = alloc(_fr_headers + _lg_headers + _term)
_nref = 0
for _o in range(0, 0x00A00000, 4):
    if struct.unpack_from('<I', rom, _o)[0] == _OLD:
        struct.pack_into('<I', rom, _o, _NEW); _nref += 1
print('v151 wild: LG headers', len(_LG), 'refs', _nref, 'added', _ADDED)

# B. event scripts (port/v151/v151.s)
import json as _js2
_MG = _js2.load(open(_P + '/data/maps/map_groups.json'))
def _all_maps():
    for _gi, _gn in enumerate(_MG['group_order']):
        for _ni in range(len(_MG[_gn])): yield _gi, _ni
def _repoint_obj_script(old, new):
    n = 0
    for g, m in _all_maps():
        ev = u32at(mapheader(g, m) + 4); cnt = rom[ev - 0x08000000]; ob = u32at(ev + 4)
        for k in range(cnt):
            if u32at(ob + 24 * k + 16) == old:
                w8(ob + 24 * k + 16, struct.pack('<I', new)); n += 1
    assert n >= 1, hex(old)
    return n
_S = lambda n: newsym[n]
# Eevee x3, both fossils
_repoint_obj_script(0x0818474B, _S('V151_EventScript_EeveeBall'))
_repoint_obj_script(0x08163ADF, _S('V151_EventScript_DomeFossil'))
_repoint_obj_script(0x08163B43, _S('V151_EventScript_HelixFossil'))
# Fighting Dojo: both Hitmonlee and Hitmonchan (the "only one" check now looks at a never-set flag)
for _a in (0x08189E6C, 0x08189EB2):
    assert rd(_a, 5) == bytes.fromhex('6a5a2b7802'), rd(_a, 5).hex()
    w8(_a + 3, struct.pack('<H', 0x0F3))
# Mew: Pokémon Mansion B1F diary
_g, _m = 1, 62
_ev = u32at(mapheader(_g, _m) + 4); _nb = rom[_ev - 0x08000000 + 3]; _bg = u32at(_ev + 16); _n = 0
for _k in range(_nb):
    if u32at(_bg + 12 * _k + 8) == 0x08168775:
        w8(_bg + 12 * _k + 8, struct.pack('<I', _S('V151_EventScript_MewDiary'))); _n += 1
assert _n == 1
# Game Corner: Pinsir (2500 coins) in the Pokémon prize list (multichoice 14)
assert rd(0x081855BC, 5) == bytes.fromhex('67e85a1808')
w8(0x081855BC, b'\x05' + struct.pack('<I', _S('V151_EventScript_ChoosePrizeMon')))
_mct = u32at(0x0809C480); _l14 = u32at(_mct + 8 * 14); assert rom[_mct + 8 * 14 + 4 - 0x08000000] == 6
_old = [rd(_l14 + 8 * i, 8) for i in range(6)]
_enc = {}
for _line in open('/home/claude/port/charmap.txt', encoding='utf-8'):
    _mm = _re.match(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$", _line.split('@')[0].strip())
    if _mm: _enc.setdefault(_mm.group(1), int(_mm.group(2), 16))
_pins = alloc(bytes(_enc[c] for c in 'カイロス') + bytes.fromhex('0000fc0600') + bytes(_enc[c] for c in '2500') + bytes.fromhex('1f02ff'))
_newl = alloc(_old[0] + _old[1] + struct.pack('<II', _pins, 0) + _old[2] + _old[3] + _old[4] + _old[5])
w8(_mct + 8 * 14, struct.pack('<IB', _newl, 7))
# Celadon Dept. Store 4F: Moon Stone 2100
assert u32at(0x08183877) == 0x08183888
w8(0x08183877, struct.pack('<I', _S('V151_Mart_Celadon4F')))
w8(0x0839BD28 + 40 * 94 + 12, struct.pack('<H', 2100))
# Bulbasaur / Charmander / Squirtle NPCs
_LAY = {l['id']: l for l in _js2.load(open(_P + '/data/layouts/layouts.json'))['layouts'] if 'id' in l}
def _elev(layout, x, y):
    l = _LAY[layout]; d = open(_P + '/' + l['blockdata_filepath'], 'rb').read()
    return struct.unpack_from('<H', d, 2 * (y * l['width'] + x))[0] >> 12
def _add_obj(g, m, layout, gfx, x, y, mt, script):
    h = mapheader(g, m); ev = u32at(h + 4); cnt = list(rom[ev - 0x08000000: ev - 0x08000000 + 4])
    old = rd(u32at(ev + 4), 24 * cnt[0]) if cnt[0] else b''
    lid = cnt[0] + 1; cnt[0] += 1
    objs = old + objtmpl(lid, gfx, x, y, _elev(layout, x, y), mt, 0, 0, script, 0)
    w8(h + 4, struct.pack('<I', alloc(bytes(cnt) + struct.pack('<IIII', alloc(objs), u32at(ev + 8), u32at(ev + 12), u32at(ev + 16)))))
    return lid
_add_obj(7, 2, 'LAYOUT_HOUSE1', 23, 9, 3, 0x09, _S('V151_EventScript_Bulbasaur'))
_add_obj(3, 43, 'LAYOUT_ROUTE24', 25, 6, 8, 0x08, _S('V151_EventScript_Charmander'))
_add_obj(3, 5, 'LAYOUT_VERMILION_CITY', 60, 17, 8, 0x08, _S('V151_EventScript_Squirtle'))
print('v151 scripts OK')
