import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
from PIL import Image
rom,st,mode,tag=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
g=Game('jp',st,rom=rom); g.run(10)
def runscript(data):
    buf=g.R['strbuf']+0x200
    for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
        for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
for f in list(range(0x820,0x828))+list(range(0x890,0x89A)): g.setflag(f)
g.setvar(0x4020,250)
sb2=g.u32(0x03004FAC)
for i,b in enumerate([0x5B,0x64,0x5C,0xFF,0xFF,0xFF,0xFF,0xFF]): g.cmd(f'poke {sb2+i:08X} {b:02X}')
if mode=='party':   # Pidgeot with Fly in slot 2
    runscript(bytes([0x79])+struct.pack('<HBHIIB',18,40,0,0,0,0)+bytes([0x7b,1,0])+struct.pack('<H',19)+b'\x02'); g.run(60)
S=[]
def sh(t): fn=f'/tmp/t16/{tag}_{mode}_{len(S)}.png'; g.shot(fn); S.append(fn)
def warp(m,x,y):
    g.teleport(m,x,y); g.run(200)
    from walker import mapid
    gr,nm=mapid('ROUTE10'); sb1=g.u32(0x03004FA8)
    for i,b in enumerate(bytes([gr,nm,0xFF,0])+struct.pack('<hh',8,20)): g.cmd(f'poke {sb1+0x24+i:08X} {b:02X}')
def downs(k):
    for i in range(k): g.cmd('tap D 1'); g.run(6)
res=''
if mode=='flash':
    warp('ROCK_TUNNEL_1F',17,4)
    sh('dark'); g.tap('S'); g.run(40); sh('menu')
    downs(5); g.run(10); sh('cursor'); g.tap('A'); g.run(240); sh('after'); g.run(400)
    g.tap('S'); g.run(40); sh('menu2'); g.tap('B'); g.run(30)
elif mode=='flycancel':
    warp('ROCK_TUNNEL_1F',17,4); g.tap('S'); g.run(40); sh('menu'); downs(4); g.tap('A'); g.run(150); sh('map')
    g.tap('B'); g.run(150); sh('cancel')
elif mode=='indoor':
    warp('VIRIDIAN_CITY_POKEMON_CENTER_1F',7,6); g.tap('S'); g.run(40); sh('menu')
    downs(4); g.tap('A'); g.run(150); sh('map'); g.tap('A'); g.run(400); sh('arrive'); res=g.pos()
elif mode=='flyrt':
    warp('ROCK_TUNNEL_1F',17,4); g.tap('S'); g.run(40); downs(4); g.tap('A'); g.run(150); sh('map')
    g.tap('D'); g.run(40); g.tap('D'); g.run(40); g.tap('D'); g.run(40); sh('cur'); g.tap('A'); g.run(500); sh('arrive'); res=g.pos()
elif mode=='town':
    warp('PALLET_TOWN',10,10); g.tap('S'); g.run(40); sh('menu')
elif mode=='party':   # party menu fly in a cave
    warp('ROCK_TUNNEL_1F',17,4); g.tap('l'); g.run(90); g.tap('D'); g.run(15); g.tap('A'); g.run(40); sh('sub')
    for i in range(4): g.tap('D'); g.run(10)
    sh('sel'); g.tap('A'); g.run(150); sh('map'); g.tap('D'); g.run(40); g.tap('D'); g.run(40); g.tap('D'); g.run(40); sh('cur'); g.tap('A'); g.run(500); sh('arrive'); res=g.pos()
print(tag,mode,res)
g.close()
W=Image.new('RGB',(240*len(S),160))
for i,f in enumerate(S): W.paste(Image.open(f).convert('RGB'),(i*240,0))
W.save(f'/tmp/t16/{tag}_{mode}.png')
