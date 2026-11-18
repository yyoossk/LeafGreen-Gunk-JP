# rewrite JP-FR ROM literals to JP-LG in place; report ambiguous ones
import re,sys,bisect
sys.path.insert(0,'/home/claude/lgtools')
from xlat import P,K,pairs
def cand(x):
    i=bisect.bisect_right(K,x)-1
    lo=P[i]; hi=P[i+1] if i+1<len(P) else lo
    return lo[1]-lo[0], hi[1]-hi[0], x-lo[0], hi[0]-x, pairs[lo[0]][0][1], pairs[hi[0]][0][1]
dry='--dry' in sys.argv
for f in [a for a in sys.argv[1:] if not a.startswith('--')]:
    src=open(f,errors='surrogateescape').read()
    out=[];last=0;n=0
    for m in re.finditer(r'0x0?8[0-9A-Fa-f]{6}\b',src):
        v=int(m.group(0),16)
        if v in (0x08000000,0x08300000) or (0x08700000<=v<0x09000000): continue
        d1,d2,dl,dh,nl,nh=cand(v)
        flag='' if d1==d2 else f'  AMBIG lo {d1} ({nl} -{dl:#x}) hi {d2} ({nh} +{dh:#x})'
        nv=v+d1
        s=m.group(0); w=len(s)-2
        ns='0x'+(f'{nv:0{w}X}' if s[2:].upper()==s[2:] else f'{nv:0{w}x}')
        line=src.count('\n',0,m.start())+1
        if flag or '--v' in sys.argv: print(f'{f}:{line}: {s} -> {ns}{flag}')
        out.append(src[last:m.start()]); out.append(ns); last=m.end(); n+=1
    out.append(src[last:])
    if not dry: open(f,'w',errors='surrogateescape').write(''.join(out))
    print(f, n, 'rewritten' if not dry else 'found', file=sys.stderr)
