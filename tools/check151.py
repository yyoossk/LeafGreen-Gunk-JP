# 151匹揃う版: where each of the 151 can be obtained (built ROM + known statics) -> table + gaps
import struct, json, re, sys
R = open(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work/port151.gba', 'rb').read()
P = '/home/claude/pret'
def u32(a): return struct.unpack_from('<I', R, a - 0x08000000)[0]
SP = {}; NAME = {}
for l in open(P + '/include/constants/species.h'):
    m = re.match(r'#define SPECIES_(\w+)\s+(\d+)\s*$', l)
    if m and int(m.group(2)) <= 151: SP[m.group(1)] = int(m.group(2))
jn = {}
sys.path.insert(0, '/home/claude/tools'); from jpdec import decode
for i in range(1, 152):
    a = 0x08245EC0 - 0x08000000  # placeholder, replaced below
OLD = 0x0838C164
first = R[OLD - 0x08000000: OLD - 0x08000000 + 20]
NEW = R.find(first, 0xB80000) + 0x08000000
J = json.load(open(P + '/src/data/wild_encounters.json'))['wild_encounter_groups'][0]
FR = [e for e in J['encounters'] if e['base_label'].endswith('_FireRed')]
src = {}
def add(sp, s):
    src.setdefault(sp, [])
    if s not in src[sp]: src[sp].append(s)
KIND = ['草むら', 'なみのり', 'いわくだき', 'つり']
mapjp = {}
for half, lab in ((0, 'FR'), (1, 'LG')):
    for i in range(132):
        h = NEW + 20 * (132 * half + i)
        mp = FR[i]['map'].replace('MAP_', '')
        for k in range(4):
            p = u32(h + 4 + 4 * k)
            if not p: continue
            arr = u32(p + 4); n = [12, 5, 5, 10][k]
            for s in range(n):
                mn, mx, sp = struct.unpack_from('<BBH', R, arr - 0x08000000 + 4 * s)
                if 1 <= sp <= 151: add(sp, f'野生({lab}) {mp} {KIND[k]}')
STATIC = {
 'BULBASAUR': '最初の3匹 / ハナダの家のおねえさん Lv10', 'CHARMANDER': '最初の3匹 / 24ばんどうろの男 Lv10',
 'SQUIRTLE': '最初の3匹 / クチバのジュンサー Lv10（オレンジバッジ）', 'EEVEE': 'タマムシマンション屋上 ×3',
 'HITMONLEE': 'かくとうどうじょう（両方）', 'HITMONCHAN': 'かくとうどうじょう（両方）', 'LAPRAS': 'シルフカンパニー',
 'MAGIKARP': '4ばんどうろの男（500円）', 'OMANYTE': 'かいのカセキ（両方もらえる）', 'KABUTO': 'こうらのカセキ（両方もらえる）',
 'AERODACTYL': 'ひみつのコハク', 'SNORLAX': '12・16ばんどうろ', 'ARTICUNO': 'ふたごじま', 'ZAPDOS': 'むじんはつでんしょ',
 'MOLTRES': 'ともしびやま', 'MEWTWO': 'ハナダのどうくつ', 'MEW': 'ポケモンやしき B1F 日記 Lv50（捕まえるまで何度でも）',
 'ELECTRODE': 'むじんはつでんしょ（ビリリダマのふり）', 'VOLTORB': 'むじんはつでんしょ（ビリリダマのふり）',
 'ABRA': 'ゲームコーナー景品', 'CLEFAIRY': 'ゲームコーナー景品', 'PINSIR': 'ゲームコーナー景品（2500枚）',
 'DRATINI': 'ゲームコーナー景品', 'SCYTHER': 'ゲームコーナー景品', 'PORYGON': 'ゲームコーナー景品'}
for k, v in STATIC.items(): add(SP[k], v)
# in-game trades (FR)
for m in re.finditer(r'\.species = SPECIES_(\w+),', open(P + '/src/data/ingame_trades.h').read()):
    if m.group(1) in SP: add(SP[m.group(1)], 'ゲーム内交換')
# evolutions (from the built ROM; trade evos are levels in this hack)
EVO = 0x08211954
how = {1: 'なつき', 2: 'なつき', 3: 'なつき', 4: 'Lv', 7: 'どうぐ'}
changed = True
while changed:
    changed = False
    for sp in range(1, 152):
        if sp not in src: continue
        ev = [struct.unpack_from('<HHH', R, EVO + 40 * sp + 8 * k - 0x08000000) for k in range(5)]
        lvtg = {tg for m, par, tg in ev if m == 4}
        for m, par, tg in ev:
            if m == 0 or tg > 151 or (m == 5 and tg in lvtg): continue
            d = f'{[n for n,v in SP.items() if v==sp][0]}から進化（{how.get(m, m)}{par if m==4 else ""}）'
            if tg not in src: src[tg] = [d]; changed = True
            elif not any('進化' in s for s in src[tg]): src[tg].append(d)
inv = {v: k for k, v in SP.items()}
gaps = [inv[i] for i in range(1, 152) if i not in src]
out = []
for i in range(1, 152):
    s = src.get(i, ['★なし'])
    wild = [x for x in s if x.startswith('野生')]
    oth = [x for x in s if not x.startswith('野生')]
    w = ''
    if wild:
        fr = sorted({x.split(' ', 1)[1] for x in wild if '(FR)' in x}); lg = sorted({x.split(' ', 1)[1] for x in wild if '(LG)' in x})
        w = '野生 ' + (f'FR:{len(fr)}か所' if fr else '') + (' ' if fr and lg else '') + (f'LG:{len(lg)}か所' if lg else '') + ' 例:' + (fr or lg)[0]
    out.append((i, inv[i], ' / '.join(([w] if w else []) + oth)))
md = ['| No. | ポケモン | 入手方法 |', '|---|---|---|']
NT = 0x1FF4B2 - 6   # JP gSpeciesNames (6 bytes each)
def jpname(i): return decode(R[NT + 6 * i: NT + 6 * i + 6])
md += ['| %d | %s | %s |' % (i, jpname(i), re.sub(r'([A-Z_]+)から', lambda m: jpname(SP[m.group(1)]) + 'から', w)) for i, n, w in out]
open('/home/claude/work/v151/table.md', 'w').write('\n'.join(md) + '\n')
json.dump(out, open('/home/claude/work/v151/table.json', 'w'), ensure_ascii=False, indent=0)
for r in out: print('%3d %-12s %s' % r)
print('GAPS:', gaps)
