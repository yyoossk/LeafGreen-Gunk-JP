# --- 赤フルカラーの機能
# island stubs live in the unused UnusedBlitBitmapRect (0x0812EEC0-0x0812F09C)
_isl=[l for l in open(PORT+'/pb/port.map') if l.startswith('.island ')][0].split(); assert int(_isl[1],16)+int(_isl[2],16)<=0x0812F09C, 'island overflow'
# つりざお: かならず かかる (Fishing6: Random() & 1 -> & 0)
assert rd(0x0805CDB2,2)==bytes.fromhex('0121'); w8(0x0805CDB2,bytes.fromhex('0021'))
# セキエイこうげんの ショップで マスターボール (10000円)
assert rd(0x08189769,5)==bytes.fromhex('8678971808'), rd(0x08189753,30).hex(); w8(0x08189769,b'\x04'+struct.pack('<I',newsym['EventScript_JpIndigoMart']))
assert r32(0x0839BEB8+40+12)==0; w8(0x0839BEB8+40+12,struct.pack('<H',10000))
# ショップの 一覧の ねだんを 5けたに (マスターボール 10000円)
assert rd(0x0809ADBC,2)==bytes.fromhex('0423'); w8(0x0809ADBC,bytes.fromhex('0523'))
assert rd(0x0809ADE2,2)==bytes.fromhex('6023'); w8(0x0809ADE2,bytes.fromhex('5a23'))
# わざを おぼえるときの「はい／いいえ」は「いいえ」から (Aの れんだで わざを うわがきしない)
assert rd(0x08024B44,4)==bytes.fromhex('04484470'); w8(0x08024B44,bytes.fromhex('04494870'))
assert rd(0x08024E74,4)==bytes.fromhex('03484470'); w8(0x08024E74,bytes.fromhex('03494870'))
assert rd(0x080D02FA,2)==bytes.fromhex('0022'); w8(0x080D02FA,bytes.fromhex('0122'))
assert rd(0x08126632,4)==bytes.fromhex('fcf779f8'); bl(0x08126632,newsym['Island_PartyYesNoDefaultNo'])
assert rd(0x081269E6,4)==bytes.fromhex('fbf79ffe'); bl(0x081269E6,newsym['Island_PartyYesNoDefaultNo'])
# バトル: わざの こうか・いりょく・めいちゅう、あいての HP (START で きりかえ)
tramp(0x0803003C,newsym['JpMoveSelectionDisplayMoveType'])
assert rd(0x0802E16E,4)==bytes.fromhex('05f01bf8'); bl(0x0802E16E,newsym['Island_ChooseMoveInput'])
# ずかん: せつめいの ページで SELECT -> 種族値と しんか
assert rd(0x081053AC,4)==bytes.fromhex('02f070f9'); bl(0x081053AC,newsym['Island_DexMonPageInput'])
# そだてや: いまの レベル
