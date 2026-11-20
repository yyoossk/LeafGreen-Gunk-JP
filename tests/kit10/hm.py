import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
from PIL import Image
rom,st=sys.argv[1],sys.argv[2]
g=Game('jp',st,rom=rom); g.run(10)
def runscript(data):
    buf=g.R['strbuf']+0x200
    for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
        for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
sc=bytes([0x79])+struct.pack('<HBHIIB',18,40,0,0,0,0)+bytes([0x7b,1,0])+struct.pack('<H',19)
for f in range(0x820,0x828): sc+=bytes([0x29])+struct.pack('<H',f)
sc+=bytes([0x44])+struct.pack('<HH',360,1)+b'\x02'
runscript(sc); g.run(60)
g.teleport('VIRIDIAN_CITY',20,20); g.run(90)
S=[]
def sh(n): g.shot(f'/tmp/t10/hm_{n}.png'); S.append(n)
# bike via R bag
g.tap('r'); g.run(90); sh('bag')
for _ in range(2): g.tap('R'); g.run(20)
sh('keyitems'); g.tap('A'); g.run(30); sh('ctx'); g.tap('A'); g.run(120); sh('bike')
p0=g.pos(); g.hold('L',16); g.run(10); print('bike move',p0,g.pos())
g.tap('l'); g.run(90); sh('party_on_bike')
g.tap('D'); g.run(15); g.tap('A'); g.run(30)
for _ in range(4): g.tap('D'); g.run(10)
sh('submenu'); g.tap('A'); g.run(150); sh('flymap'); g.tap('A'); g.run(400); sh('flown')
print('after fly',g.pos())
g.close()
W=Image.new('RGB',(240*len(S),160))
for i,n in enumerate(S): W.paste(Image.open(f'/tmp/t10/hm_{n}.png').convert('RGB'),(i*240,0))
W.save('/tmp/t10/hm.png')
