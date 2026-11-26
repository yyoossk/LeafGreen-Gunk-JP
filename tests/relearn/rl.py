import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom,st,sp,lv,tag=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
g=Game('jp',st,rom=rom); g.run(10)
def runscript(data):
    buf=g.R['strbuf']+0x200
    for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
        for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
s=bytes([0x79])+struct.pack('<HBHIIB',sp,lv,0,0,0,0)
s+=bytes([0x16])+struct.pack('<HH',0x8004,1)+bytes([0x25])+struct.pack('<H',224)+bytes([0x27,0x02])
runscript(s); g.run(200); print("cnt",g.u8(g.R["cnt"]),hex(g.cb2()),g.peek(0x03000EA8,0x18).hex()); g.shot(f'/tmp/rl/{tag}0.png')
for i in range(3):
    g.hold('D',1); g.run(1)
for i in range(1,4):
    for k in range(4): g.tap('D')
    g.run(10); g.shot(f'/tmp/rl/{tag}{i}.png')
g.peek(0,1); g.close()
