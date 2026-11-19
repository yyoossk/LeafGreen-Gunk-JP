import re, base64, io
from PIL import Image
s=open('/home/claude/fr_blog.html',encoding='utf-8').read()
def pair(a,b):
    W=Image.new('RGB',(488,160),(255,255,255)); W.paste(Image.open(a).convert('RGB'),(0,0)); W.paste(Image.open(b).convert('RGB'),(248,0)); return W
def one(a): return Image.open(a).convert('RGB')
C='/tmp/cap/'; BT='/tmp/bt/'; WK='/tmp/walk/'; T='/tmp/t151/'
imgs=[Image.open('/tmp/blog/header.jpg'),
 pair(C+'fol1.png',C+'fol2.png'),
 pair(C+'cut2.png',C+'cut3.png'),
 one(C+'party.png'),
 one(C+'mpc1.png'),
 pair(C+'bag1.png',C+'bag4.png'),
 one(C+'bag2.png'),
 one(C+'wild.png'),
 pair(C+'sum1.png',C+'sum2.png'),
 one(C+'sum3.png'),
 pair(BT+'jp_003_menu.png',BT+'jp_005_arrive.png'),
 pair(BT+'jp_013_desk.png',BT+'jp_104_fight.png'),
 one(BT+'jp_115_between.png'),
 pair(WK+'jp_00003.png',WK+'jp_00026.png'),
 pair(WK+'jp_00028_b.png',WK+'jp_00032.png'),
 pair(WK+'jp_00035.png',WK+'jp_00038.png'),
 one(WK+'jp_00048.png'),
 pair(WK+'jp_00017_d.png',C+'nv7.png'),
 one(C+'tm0.png'),
 pair(T+'oy_3.png',T+'sq1_02.png'),
 pair(T+'mew1_06.png',T+'mew1_battle.png'),
 pair(T+'fossil_12.png',T+'pq_0.png')]
it=iter(imgs)
def rep(m):
    im=next(it); bio=io.BytesIO()
    if m.group(1)=='jpeg': im.convert('RGB').save(bio,'JPEG',quality=88)
    else: im.save(bio,'PNG',optimize=True)
    return 'src="data:image/%s;base64,%s"'%(m.group(1),base64.b64encode(bio.getvalue()).decode())
s=re.sub(r'src="data:image/(\w+);base64,[^"]+"',rep,s)
assert next(it,None) is None
# text: swap FireRed <-> LeafGreen (Japanese names)
s=s.replace('ファイアレッド','\x01').replace('リーフグリーン','\x02').replace('\x01','リーフグリーン').replace('\x02','ファイアレッド')
s=s.replace('FireRed-Gunk-JP','LeafGreen-Gunk-JP')
for a,b in [('3B2056E9','0A48556B'),('BB640DF7','8DA4601A'),('34636886','3AC2FE34'),('B93B2766','1481AE24')]: s=s.replace(a,b)
s=s.replace('カイロス','ストライク').replace('2500枚','5500枚')
for a,b in [('#d00','#2a8a2a'),('#c00','#1f6f1f'),('#f2b0b0','#a8d8a0'),('#fff4f4','#f2fbef')]: s=s.replace(a,b)
open('/tmp/blog/draft.html','w',encoding='utf-8').write(s)
