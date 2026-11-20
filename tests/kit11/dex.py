import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
from PIL import Image
rom,st,mapn,x,y,tag=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
g=Game('jp',st,rom=rom); g.run(10)
def runscript(data):
    buf=g.R['strbuf']+0x200
    for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
        for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
runscript(bytes([0x79])+struct.pack('<HBHIIB',129,5,0,0,0,0)+b'\x02'); g.run(60)
g.teleport(mapn,x,y); g.run(120)
S=[]
def sh(n): g.shot(f'/tmp/t11/{tag}_{n}.png'); S.append(n)
g.tap('S'); g.run(40); g.tap('A'); g.run(90); sh('dex0')
g.tap('A'); g.run(90); sh('dex1')
for i in range(130): g.cmd('tap D 1')
g.run(30); sh('list'); g.tap('A'); g.run(90); sh('entry'); g.tap('A'); g.run(10)
for i in range(4): sh(f'area{i}'); g.run(11)
g.close()
W=Image.new('RGB',(240*len(S),160))
for i,n in enumerate(S): W.paste(Image.open(f'/tmp/t11/{tag}_{n}.png').convert('RGB'),(i*240,0))
W.save(f'/tmp/t11/{tag}.png')
