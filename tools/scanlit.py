import re,sys,os
sys.path.insert(0,'/home/claude/lgtools')
from xlat import fr2lg
files=sys.argv[1:]
tot=0
for f in files:
    for i,l in enumerate(open(f,errors='replace'),1):
        for m in re.finditer(r'0x0?8[0-9A-Fa-f]{6}\b',l):
            v=int(m.group(0),16)
            if v<0x08000000 or v>=0x08700000 and v<0x09000000 and (v>>20)&0xF>=7: continue
            if v in (0x08000000,0x08300000): continue
            tot+=1
            print(f'{f}:{i}: {m.group(0)} -> {fr2lg(v):#010x}  | {l.strip()[:110]}')
print('total',tot,file=sys.stderr)
