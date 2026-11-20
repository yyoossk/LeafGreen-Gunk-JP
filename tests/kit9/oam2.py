import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom,st,tag=sys.argv[1],sys.argv[2],sys.argv[3]
g=Game('jp',st,rom=rom); g.run(10)
def runscript(data):
    buf=g.R['strbuf']+0x200
    for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
        for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
runscript(bytes([0x25,60,0,0x27,0x02])); g.run(120)
NDOWN=int(sys.argv[4]) if len(sys.argv)>4 else 2
for _ in range(NDOWN): g.tap('D'); g.run(10)
g.tap('A'); g.run(150)
def oam():
    b=g.peek(0x07000000,8*40); out=[]
    for i in range(40):
        a0,a1,a2=struct.unpack('<HHH',b[i*8:i*8+6])
        if (a0>>8)&3==2: continue
        out.append((a0&0xFF,a1&0x1FF,a2&0x3FF))
    return out
def track(n):
    seq=[oam() for _ in range(n) if not g.run(2)]
    # entries keyed by (x,tile)
    keys={}
    for f,o in enumerate(seq):
        for (y,x,t) in o: keys.setdefault((x,y),[]).append(t)
    return {k:v for k,v in keys.items() if len(set(v))>1}
print(tag,'idle',track(30))
for mv in ['R','U','D','L']:
    g.tap(mv); g.run(20); print(tag,'after move',mv,track(30))
g.close()
