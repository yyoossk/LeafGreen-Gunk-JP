import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
from PIL import Image
rom,st,tag=sys.argv[1],sys.argv[2],sys.argv[3]
g=Game('jp',st,rom=rom); g.run(10)
def runscript(data):
    buf=g.R['strbuf']+0x200
    for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
        for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
runscript(bytes([0x79])+struct.pack('<HBHIIB',129,5,0,0,0,0)+b'\x02'); g.run(60)
g.teleport('VIRIDIAN_CITY',20,20); g.run(120); g.shot(f'/tmp/t11/{tag}_before.png')
g.tap('S'); g.run(40); g.tap('A'); g.run(90); g.tap('A'); g.run(90)
for i in range(130): g.cmd('tap D 1')
g.run(30)
for r in range(4):
    g.tap('A'); g.run(80); g.tap('A'); g.run(80); g.tap('B'); g.run(60); g.tap('B'); g.run(60)
g.shot(f'/tmp/t11/{tag}_list.png')
for i in range(5): g.tap('B'); g.run(80)
g.run(60); g.shot(f'/tmp/t11/{tag}_after.png')
g.hold('L',32); g.run(20); g.shot(f'/tmp/t11/{tag}_walk.png')
g.close()
W=Image.new('RGB',(960,160))
for i,n in enumerate(['before','list','after','walk']): W.paste(Image.open(f'/tmp/t11/{tag}_{n}.png').convert('RGB'),(i*240,0))
W.save(f'/tmp/t11/{tag}.png')
