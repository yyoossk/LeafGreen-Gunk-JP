# FRLG+ Master Trainers -> JP port data generator
# outputs: port/src/hooks/gen/master_data.h, port/data/hooks/master_trainers.s, work/master_place.json
import re, json
F = '/home/claude/frlgplus/'
P = '/home/claude/pret/'
OUT_H = '/home/claude/port/src/hooks/gen/master_data.h'
OUT_S = '/home/claude/port/data/hooks/master_gen.inc'
OUT_J = '/home/claude/work/master_place.json'

# ---- trainer headers
h = open(F + 'src/data/master_trainers.h').read()
ents = re.findall(r'\[(MASTER_\w+)\] = \{(.*?)\n    \},', h, re.S)
mo = open(F + 'include/constants/master_opponents.h').read()
mid = {k: int(v) for k, v in re.findall(r'#define (MASTER_\w+) (\d+)', mo)}
parties = open(F + 'src/data/master_trainer_parties.h').read()
pblocks = dict(re.findall(r'sParty_(Master\w+)\[\] = \{(.*?)\n\};', parties, re.S))
sp_h = open(P + 'include/constants/species.h').read()
SPECIES = {k: int(v) for k, v in re.findall(r'#define (SPECIES_\w+)\s+(\d+)', sp_h)}

CLASS_ID = {'LASS': 59, 'COOLTRAINER': 86, 'BEAUTY': 73, 'SWIMMER_F': 74, 'BUG_CATCHER': 58, 'BIRD_KEEPER': 79,
            'YOUNGSTER': 57, 'SCIENTIST': 82, 'HIKER': 65, 'BLACK_BELT': 80, 'PSYCHIC': 75}
SCRIPT_CLASS = {'LASS': 0, 'BEAUTY': 0, 'SWIMMER_F': 0, 'BIRD_KEEPER': 1, 'COOLTRAINER': 1, 'BLACK_BELT': 2, 'HIKER': 2,
                'BUG_CATCHER': 3, 'YOUNGSTER': 3, 'PSYCHIC': 4, 'SCIENTIST': 4}
MUSIC = {'TRAINER_ENCOUNTER_MUSIC_FEMALE | F_TRAINER_FEMALE': 0x81, 'TRAINER_ENCOUNTER_MUSIC_COOL': 5,
         'TRAINER_ENCOUNTER_MUSIC_MALE': 0, 'TRAINER_ENCOUNTER_MUSIC_INTENSE': 4,
         'TRAINER_ENCOUNTER_MUSIC_SUSPICIOUS': 3, 'TRAINER_ENCOUNTER_MUSIC_HIKER': 11}
# new JP trainer pics, appended after the 148 vanilla ones
NEWPICS = ['BEAUTY', 'BIRD_KEEPER', 'BLACK_BELT', 'BUG_CATCHER', 'COOLTRAINER_M', 'HIKER', 'LASS', 'PSYCHIC_M', 'SCIENTIST', 'YOUNGSTER', 'SWIMMER']
PIC_ID = {'TRAINER_PIC_MASTER_' + n: 148 + i for i, n in enumerate(NEWPICS)}
NAMES = dict(BULBASAUR='レナ', IVYSAUR='カトリーナ', VENUSAUR='サリー', CHARMANDER='ティム', CHARMELEON='クリス', CHARIZARD='エドモンド',
    SQUIRTLE='スージー', WARTORTLE='プリタ', BLASTOISE='テッサ', CATERPIE='ジェイク', METAPOD='ブライソン', BUTTERFREE='ボビー',
    WEEDLE='スコット', KAKUNA='ケニー', BEEDRILL='テリー', PIDGEY='ルーイ', PIDGEOTTO='ハウイー', PIDGEOT='ワイアット',
    RATTATA='ブレット', RATICATE='デニス', SPEAROW='ラルフ', FEAROW='セオ', EKANS='ハーバート', ARBOK='アダム', PIKACHU='イクエ',
    RAICHU='ロッテ', SANDSHREW='ポール', SANDSLASH='ベン', NIDORAN_F='ロニー', NIDORINA='フレッド', NIDOQUEEN='パーシー',
    NIDORAN_M='アルビン', NIDORINO='デイブ', NIDOKING='カールトン', CLEFAIRY='チェル', CLEFABLE='サンドラ', VULPIX='フィン',
    NINETALES='アーノルド', JIGGLYPUFF='マージ', WIGGLYTUFF='ユミ', ZUBAT='ウエスト', GOLBAT='キートン', ODDISH='エイミー',
    GLOOM='エマ', VILEPLUME='サトコ', PARAS='エバン', PARASECT='ハンス', VENONAT='オリー', VENOMOTH='ラヨシュ', DIGLETT='コリン',
    DUGTRIO='デクスター', MEOWTH='ケン', PERSIAN='ショーン', PSYDUCK='ニコル', GOLDUCK='カミーユ', MANKEY='タダシ', PRIMEAPE='カノウ',
    GROWLITHE='オースチン', ARCANINE='サッチ', POLIWAG='ビッキー', POLIWHIRL='キンバリー', POLIWRATH='ユエン', ABRA='アンジェロ',
    KADABRA='ハイメ', ALAKAZAM='フレイザー', MACHOP='マサヒロ', MACHOKE='リュウジ', MACHAMP='ランディ', BELLSPROUT='ハナ',
    WEEPINBELL='エミリー', VICTREEBEL='ダイアン', TENTACOOL='フランシス', TENTACRUEL='メルビン', GEODUDE='アーウィン',
    GRAVELER='ディラン', GOLEM='バレンチノ', PONYTA='ギャレット', RAPIDASH='レイモンド', SLOWPOKE='ジル', SLOWBRO='ハルカ',
    MAGNEMITE='マレー', MAGNETON='ジュリアン', FARFETCHD='モー', DODUO='バーニー', DODRIO='シーモア', SEEL='アイナ', DEWGONG='ロイス',
    GRIMER='コリー', MUK='ゴードン', SHELLDER='シェリー', CLOYSTER='ローズ', GASTLY='アリン', HAUNTER='ダニー', GENGAR='ロス',
    ONIX='ジム', DROWZEE='アントン', HYPNO='ブラド', KRABBY='カール', KINGLER='レオポルド', VOLTORB='ハンフリー', ELECTRODE='エルトン',
    EXEGGCUTE='サマー', EXEGGUTOR='シンディ', CUBONE='リヒター', MAROWAK='ジュリアス', HITMONLEE='チェン', HITMONCHAN='ウォン',
    LICKITUNG='シド', KOFFING='アルバート', WEEZING='ドニー', RHYHORN='ファルカス', RHYDON='ユージン', CHANSEY='ミズキ',
    TANGELA='ハーリーン', KANGASKHAN='マック', HORSEA='ビバリー', SEADRA='ルーシー', GOLDEEN='エベット', SEAKING='アリアナ',
    STARYU='ジョー', STARMIE='ハリソン', MR_MIME='ルイ', SCYTHER='ルーイー', JYNX='エイブリー', ELECTABUZZ='リーバイ', MAGMAR='ジェイス',
    PINSIR='リョウタ', TAUROS='ジャクソン', MAGIKARP='イーストン', GYARADOS='ドミニク', LAPRAS='ヘイゼル', EEVEE='アオイ',
    VAPOREON='ユエ', JOLTEON='アルフォン', FLAREON='ダックス', PORYGON='ジョーダン', OMANYTE='コルソン', OMASTAR='ライオネル',
    KABUTO='バーナビー', KABUTOPS='ケンジ', AERODACTYL='ヒサト', SNORLAX='ジェイ', DRATINI='ジラード', DRAGONAIR='アルジュン',
    DRAGONITE='グレイソン')
NATURES = ['HARDY', 'LONELY', 'BRAVE', 'ADAMANT', 'NAUGHTY', 'BOLD', 'DOCILE', 'RELAXED', 'IMPISH', 'LAX', 'TIMID', 'HASTY', 'SERIOUS',
           'JOLLY', 'NAIVE', 'MODEST', 'MILD', 'QUIET', 'BASHFUL', 'RASH', 'CALM', 'GENTLE', 'SASSY', 'CAREFUL', 'QUIRKY']
NOBATTLE = [132, 144, 145, 146, 150, 151]

def parse_mons(block):
    mons = []
    for m in re.findall(r'\{(.*?)\n    \}', block, re.S):
        g = lambda k: re.search(r'\.%s = ([^,\n]+)' % k, m).group(1).strip()
        evs = re.search(r'\.evs = \{([^}]*)\}', m).group(1)
        mv = re.search(r'\.moves = \{([^}]*)\}', m).group(1)
        mons.append(dict(iv=int(g('iv')), lvl=int(g('lvl')), evs=[int(x) for x in evs.split(',')],
                         nature=NATURES.index(g('nature').replace('NATURE_', '')), species=g('species'),
                         item=g('heldItem'), ability=int(g('abilityNum')), moves=[x.strip() for x in mv.split(',')]))
    return mons

trainers = {}
for k, b in ents:
    if k == 'MASTER_NONE': continue
    sp = mid[k]
    cl = re.search(r'trainerClass = TRAINER_CLASS_(\w+)', b).group(1)
    if cl == 'PKMN_TRAINER': continue
    music = MUSIC[re.search(r'encounterMusic_gender = ([^,]+),', b).group(1).strip()]
    pic = PIC_ID[re.search(r'trainerPic = (\w+)', b).group(1)]
    pn = re.search(r'party = CUSTOM_MOVES_EVS\(sParty_(\w+)\)', b).group(1)
    mon = parse_mons(pblocks[pn])[0]
    assert SPECIES[mon['species']] == sp, (k, mon['species'])
    trainers[sp] = dict(key=k[7:], cls=CLASS_ID[cl], scls=SCRIPT_CLASS[cl], music=music, pic=pic, name=NAMES[k[7:]], mon=mon)
assert len(trainers) == 145 and not set(trainers) & set(NOBATTLE)

oak = parse_mons(re.search(r'sParty_MasterOak\[\] = \{(.*?)\n\};', open(F + 'src/data/trainer_parties.h').read(), re.S).group(1))

def cmon(m, lvl=True):
    s = '{%d, %d, %d, %d, {%s}, %s, %s, {%s}}' % (m['iv'], m['nature'], m['ability'], m['lvl'] if lvl else 0,
        ', '.join(map(str, m['evs'])), m['species'], m['item'], ', '.join(m['moves']))
    return s

with open(OUT_H, 'w') as f:
    f.write('// generated by tools/gen_master.py from FRLG+ src/data/master_trainers.h, master_trainer_parties.h\n')
    f.write('// iv, nature, abilityNum, lvl, evs[6], species, heldItem, moves[4]\n')
    f.write('static const struct JpMasterMon sMasterMons[152] = {\n')
    for sp in sorted(trainers):
        f.write('    [%d] = %s, // %s\n' % (sp, cmon(trainers[sp]['mon']), trainers[sp]['key']))
    f.write('};\n')
    f.write('// script class (0 lass/beauty/swimmer, 1 bird keeper/cooltrainer, 2 black belt/hiker, 3 bug catcher/youngster, 4 psychic/scientist); 0xFF = none\n')
    sc = [0xFF] * 152
    for sp, t in trainers.items(): sc[sp] = t['scls']
    for sp in NOBATTLE: sc[sp] = 4
    f.write('static const u8 sMasterScriptClass[152] = {%s};\n' % ', '.join(map(str, sc)))
    gd = [0] * 152
    for sp, t in trainers.items(): gd[sp] = 0xFE if t['music'] & 0x80 else 0
    f.write('static const u8 sMasterGender[152] = {%s};\n' % ', '.join(map(str, gd)))
    f.write('static const struct JpMasterMon sOakMons[6] = {\n%s\n};\n' % ',\n'.join('    ' + cmon(m) for m in oak))

# ---- scripts
S = []
S.append('@ generated by tools/gen_master.py\n')
S.append('\t.global gJpMasterScripts\n\t.align 2\ngJpMasterScripts:\n')
for sp in range(152):
    if sp in trainers or sp in NOBATTLE: S.append('\t.4byte JpMaster_EventScript_%d\n' % sp)
    else: S.append('\t.4byte 0\n')
for sp in range(1, 152):
    if sp in NOBATTLE:
        S.append('JpMaster_EventScript_%d::\n\tsetvar TRAINER, %d\n\tgoto JpMaster_EventScript_NoBattle\n' % (sp, sp))
    elif sp in trainers:
        c = trainers[sp]['scls']
        S.append('JpMaster_EventScript_%d::\n\tsetvar TRAINER, %d\n\tcall JpMaster_EventScript_Pre\n'
                 '\ttrainerbattle_no_intro JP_MASTER_BASE + %d, JpMaster_Text_BattleLoss%d\n'
                 '\tsetvar TRAINER, %d\n\tgoto JpMaster_EventScript_Post\n' % (sp, sp, sp - 1, c, sp))
open(OUT_S, 'w').write(''.join(S))

# ---- trainer table entries + placements for patch_port
mg = json.load(open(P + 'data/maps/map_groups.json'))
idx = {}
for gi, gn in enumerate(mg['group_order']):
    for ni, m in enumerate(mg[gn]): idx[m] = (gi, ni)
GFX = {'OBJ_EVENT_GFX_MASTER_' + n: 160 + i for i, n in enumerate(['BEAUTY', 'BIRD_KEEPER', 'BLACK_BELT', 'BUG_CATCHER', 'COOLTRAINER_M', 'HIKER', 'LASS', 'PSYCHIC_M', 'SCIENTIST', 'YOUNGSTER'])}
GFX['OBJ_EVENT_GFX_SWIMMER_F_WATER'] = 44
MT = {'MOVEMENT_TYPE_NONE': 0, 'MOVEMENT_TYPE_FACE_UP': 7, 'MOVEMENT_TYPE_FACE_DOWN': 8, 'MOVEMENT_TYPE_FACE_LEFT': 9, 'MOVEMENT_TYPE_FACE_RIGHT': 10}
DY = {'Route12': 1}   # FRLG+ removed the top row of Route 12
place = []
import glob
for fn in sorted(glob.glob(F + 'data/maps/*/map.json')):
    m = json.load(open(fn))
    for o in m.get('object_events', []):
        s = o.get('script', '')
        if not s.startswith('MasterTrainer_EventScript_'): continue
        key = s[len('MasterTrainer_EventScript_'):].upper().replace('NIDORANF', 'NIDORAN_F').replace('NIDORANM', 'NIDORAN_M').replace('MRMIME', 'MR_MIME')
        sp = mid['MASTER_' + key]
        g, n = idx[m['name']]
        place.append(dict(map=m['name'], g=g, n=n, sp=sp, gfx=GFX[o['graphics_id']], x=o['x'], y=o['y'] + DY.get(m['name'], 0),
                          elev=o['elevation'], mt=MT[o['movement_type']]))
assert len(place) == 151 and len({p['sp'] for p in place}) == 151
tr = {sp: dict(cls=t['cls'], music=t['music'], pic=t['pic'], name=t['name'], species=t['mon']['species']) for sp, t in trainers.items()}
json.dump(dict(trainers=tr, place=place, newpics=NEWPICS), open(OUT_J, 'w'), ensure_ascii=False, indent=0)
print('trainers', len(trainers), 'placements', len(place), 'maps', len({p['map'] for p in place}))
