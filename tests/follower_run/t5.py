import sys,struct,hashlib; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom=sys.argv[1]; st=sys.argv[2]; seq=sys.argv[3]
g=Game('jp',st,rom=rom); g.run(10); g.setflag(0x82F); g.setvar(0x4020,250)
g.teleport('VIRIDIAN_CITY',20,20); g.run(300)
GS=0x020205B8
names={}; s=[]
for part in seq.split(','):
    k,n=part.split(':')
    for i in range(int(n)):
        g.cmd(f'hold {k} 1' if k!='-' else 'run 1')
        d=g.peek(GS+3*0x44,0x44); t=struct.unpack_from('<H',d,4)[0]&0x3FF
        an=d[0x2A]; ai=d[0x2B]; ad=d[0x2C]
        h=hashlib.md5(g.peek(0x06010000+t*32,512)).hexdigest()
        c=names.setdefault(h,chr(65+len(names)))
        s.append(f'{c}{an}.{ai}')
print(' '.join(s))
g.close()
