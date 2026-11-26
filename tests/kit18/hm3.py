# kit 18: スタートメニューの ひでんわざ・でるポケモン、ずかんの でるポケモン
import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
from PIL import Image
rom,st,mode,tag=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
g=Game('jp',st,rom=rom); g.run(10)
for f in list(range(0x820,0x828))+list(range(0x890,0x89A))+[0x829]: g.setflag(f)
g.setvar(0x4020,250)
sb2=g.u32(0x03004FAC)
for i,b in enumerate([0x5B,0x64,0x5C,0xFF,0xFF,0xFF,0xFF,0xFF]): g.cmd(f'poke {sb2+i:08X} {b:02X}')   # なまえ
S=[]
def sh(): fn=f'/tmp/t18/{tag}_{mode}_{len(S)}.png'; g.shot(fn); S.append(fn)
def warp(m,x,y):
    g.teleport(m,x,y); g.run(200)
    from walker import mapid
    gr,nm=mapid('ROUTE10'); sb1=g.u32(0x03004FA8)
    for i,b in enumerate(bytes([gr,nm,0xFF,0])+struct.pack('<hh',8,20)): g.cmd(f'poke {sb1+0x24+i:08X} {b:02X}')
def downs(k):
    for i in range(k): g.cmd('tap D 1'); g.run(6)
res=''
if mode=='town':
    warp('ROUTE12',14,20)
    g.tap('S'); g.run(40); sh(); downs(4); g.tap('A'); g.run(30); sh(); g.tap('B'); g.run(30); sh()
    downs(1); g.tap('A'); g.run(60); sh(); downs(4); sh(); g.tap('B'); g.run(60); sh()
    g.tap('B'); g.run(30); g.cmd('hold U 20'); g.run(20); sh(); res=g.pos()
elif mode=='cave':
    warp('ROCK_TUNNEL_1F',17,4)
    g.tap('S'); g.run(40); downs(4); g.tap('A'); g.run(30); sh(); downs(1); g.tap('A'); g.run(400); sh()
    g.tap('S'); g.run(40); sh(); g.tap('B'); g.run(30)
    g.tap('S'); g.run(40); g.tap('A'); g.run(30); sh(); g.tap('A'); g.run(150); sh(); g.tap('D'); g.run(40); g.tap('D'); g.run(40); g.tap('D'); g.run(40); sh(); g.tap('A'); g.run(500); sh(); res=g.pos()
elif mode=='lit':
    warp('MT_MOON_1F',14,10); g.tap('S'); g.run(40); sh(); downs(5); g.tap('A'); g.run(60); sh(); downs(6); sh(); g.tap('A'); g.run(60); sh()
elif mode=='indoor':
    warp('VIRIDIAN_CITY_POKEMON_CENTER_1F',7,6); g.tap('S'); g.run(40); sh(); downs(5); g.tap('A'); g.run(60); sh(); g.tap('B'); g.run(60); sh()
elif mode.startswith('dex'):
    m={'dex':('ROUTE12',14,20),'dexcave':('CERULEAN_CAVE_1F',10,10),'dex1':('ROUTE1',10,10)}[mode]
    warp(*m)
    # つかまえた（こい色）を 見るため：ポッポ(16) と コイキング(129) を もらう
    def runscript(data):
        buf=g.R['strbuf']+0x200
        for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
        for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
            for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
    runscript(b''.join(bytes([0x79])+struct.pack('<HBHIIB',sp,5,0,0,0,0) for sp in (16,129))+b'\x02'); g.run(60)
    g.tap('S'); g.run(60); g.tap('A'); g.run(200)
    for i in range(14): g.cmd('tap D 1'); g.run(4)
    g.run(10); sh(); g.tap('A'); g.run(30); sh()
    for i in range(6): g.cmd('tap D 1'); g.run(4)
    sh(); g.tap('B'); g.run(30); sh(); g.tap('B'); g.run(120); sh()
print(tag,mode,res)
g.close()
W=Image.new('RGB',(240*len(S),160))
for i,f in enumerate(S): W.paste(Image.open(f).convert('RGB'),(i*240,0))
W.save(f'/tmp/t18/{tag}_{mode}.png')
