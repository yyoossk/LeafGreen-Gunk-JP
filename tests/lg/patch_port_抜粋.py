# --- メニューから パソコン (start menu item 9)
tramp(0x0806E51C,newsym['JpSetUpStartMenu_NormalField'])
assert rd(0x0806EB00,4)==bytes.fromhex('00b50848'); tramp(0x0806EB00,newsym['JpStartMenu_FadeScreenIfLeavingOverworld'])
_na=alloc(rd(0x08366B34,72)+struct.pack('<II',newsym['gJpText_MenuPC'],newsym['JpStartMenuPcCallback']|1))
for _r in (0x0806E708,0x0806EAE0,0x0806EB60):
    assert u32at(_r)==0x08366B34; w8(_r,struct.pack('<I',_na))
_nd=alloc(rd(0x08366B84,36)+struct.pack('<I',newsym['gJpStartMenuDesc_PC']))
for _r in (0x0806E8A4,0x0806EAD4):
    assert u32at(_r)==0x08366B84; w8(_r,struct.pack('<I',_nd))
assert rd(0x08193ECE,5)==bytes.fromhex('1604800000')
w8(0x08193ECE,b'\x05'+struct.pack('<I',newsym['EventScript_JpTurnOffPC']))
# --- ランニングシューズは おかあさんから
assert rd(0x0817F43E,11)==bytes.fromhex('166c400100292e002a9200')
w8(0x0817F43E,b'\x04'+struct.pack('<I',newsym['EventScript_JpBrockScene'])+bytes(6))
225-_ev=u32at(mapheader(4,0)+4); _ob=u32at(_ev+4)
226:assert u32at(_ob+16)==0x0817B879; w8(_ob+16,struct.pack('<I',newsym['EventScript_JpMom']))
