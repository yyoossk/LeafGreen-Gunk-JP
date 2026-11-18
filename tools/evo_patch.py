import re
def consts(path):
    d={}
    for l in open(path):
        m=re.match(r'#define\s+(\w+)\s+(\d+|0x[0-9A-Fa-f]+)\b',l)
        if m: d[m.group(1)]=int(m.group(2),0)
    return d
C={}
for p in ['/home/claude/pret/include/constants/species.h','/home/claude/pret/include/constants/items.h','/home/claude/pret/include/constants/pokemon.h']: C.update(consts(p))
def parse(path):
    s=open(path).read(); out={}
    for m in re.finditer(r'\[(SPECIES_\w+)\]\s*=\s*\{(.*?)\}\},',s,re.S):
        ents=re.findall(r'\{(EVO_\w+),\s*(\w+),\s*(SPECIES_\w+)\}',m.group(2))
        out[m.group(1)]=[(C[a],C.get(b, int(b) if b.isdigit() else None),C[c]) for a,b,c in ents]
    return out
def additions():
    a=parse('/home/claude/pret/src/data/pokemon/evolution.h'); b=parse('/home/claude/gunk/src/data/pokemon/evolution.h')
    res=[]
    for sp,ents in b.items():
        for e in ents:
            if e not in a.get(sp,[]): res.append((C[sp],e))
    return res
if __name__=='__main__':
    for x in additions(): print(x)
