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
for b0 in range(10,50,8):
    sc=b''
    for sp in range(b0,b0+8): sc+=bytes([0x79])+struct.pack('<HBHIIB',sp,5,0,0,0,0)
    runscript(sc+b'\x02'); g.run(60)
g.teleport('ROUTE10_POKEMON_CENTER_1F',12,6); g.run(90); g.tap('U'); g.run(20)
def talk(n,pre):
    g.tap('A'); g.run(40)
    for i in range(n):
        g.shot(f'/tmp/t8/{tag}{pre}{i:02d}.png'); g.tap('A'); g.run(45)
talk(24,'a')
print(tag,'flag 0x2FA',g.getflag(0x2FA))
g.run(60); talk(8,'b')
print(tag,'flag 0x2FA after 2nd',g.getflag(0x2FA))
g.close()
W=Image.new('RGB',(240*8,160*4))
for i in range(24): W.paste(Image.open(f'/tmp/t8/{tag}a{i:02d}.png').convert('RGB'),((i%8)*240,(i//8)*160))
for i in range(8): W.paste(Image.open(f'/tmp/t8/{tag}b{i:02d}.png').convert('RGB'),(i*240,480))
W.save(f'/tmp/t8/{tag}.png')
