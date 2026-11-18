import pickle, struct, bisect, collections
US=open('/home/claude/pret/pokeleafgreen_rev1.gba','rb').read()
JP=open('/home/claude/roms/Pocket Monsters - LeafGreen (Japan) (Rev 1).gba','rb').read()
syms=[]
for line in open('/home/claude/work/us.nm'):
    p=line.split()
    if len(p)==3: syms.append((int(p[0],16),p[1],p[2]))
named=[s for s in syms if not s[2].startswith('.') and s[1] not in 'aA' or (s[1] in 'aA' and False)]
named=sorted([s for s in syms if not s[2].startswith('.') and not s[2].startswith('$')])
saddr=[s[0] for s in named]
def owner(v):
    i=bisect.bisect_right(saddr,v)-1
    if i<0: return None
    return named[i]
fm=pickle.load(open('/home/claude/work/fmatch.pkl','rb'))
funcs=sorted(fm)
walked={}
amap={}   # US addr -> JP addr (symbol starts)
votes=collections.defaultdict(collections.Counter)
for a,(n,j,sz) in fm.items():
    if j: amap[a]=j
def rd(b,o): return struct.unpack_from('<I',b,o-0x08000000)[0]
def hw(b,o): return b[o-0x08000000]|b[o-0x08000000+1]<<8
def walk(a,j,sz):
    i=0
    while i+3<sz:
        h1=hw(US,a+i);h2=hw(US,a+i+2)
        if (h1&0xF800)==0xF000 and (h2&0xF800)==0xF800:
            def tgt(B,o):
                x1=hw(B,o);x2=hw(B,o+2)
                off=((x1&0x7FF)<<12)|((x2&0x7FF)<<1)
                if off&0x400000: off-=0x800000
                return o+4+off
            votes[tgt(US,a+i)][tgt(JP,j+i)]+=1
            i+=4; continue
        i+=2
    for i in range((-a)%4, sz-3, 4):
        w=rd(US,a+i)
        if (w>>24) in (2,3,8,9):
            v=rd(JP,j+i)
            o=owner(w&~1 if (w>>24) in (8,9) else w)
            if o is None: continue
            delta=w-o[0]
            votes[o[0]][v-delta]+=1
from match import mask as _mask
import match as _m
def ext(a):
    j=a
    while True:
        nx=_m.nexta.get(j)
        if nx is None or nx>=0x081EA000 or nx in _m.funcs: return (nx or a+4)-a
        j=nx
for rnd in range(4):
    for a,j in list(amap.items()):
        if (a>>24)!=8 or a>=0x081EA000 or (a&~1) not in _m.funcs: continue
        a2=a&~1; j2=j&~1
        sz=ext(a2)
        if sz>0x4000: continue
        if walked.get(a2)==j2: continue
        ub=US[a2-0x08000000:a2-0x08000000+sz]; jb=JP[j2-0x08000000:j2-0x08000000+sz]
        if (a2%4)==(j2%4) and _mask(ub,a2)==_mask(jb,j2):
            walk(a2,j2,sz); walked[a2]=j2
    added=0
    for u,c in votes.items():
        if u not in amap:
            (jv,cnt),=c.most_common(1)
            if cnt>=1 and (len(c)==1 or cnt>=2*sum(c.values())//3+1):
                amap[u]=jv; added+=1
    # neighbor alignment for function list
    fl=sorted(fm)
    for k in range(len(fl)-1):
        a,b=fl[k],fl[k+1]
        if a in amap and b not in amap and b in fm:
            n,j,sz=fm[b]
            cand=amap[a]+(b-a)
            # verify byte-equal masked roughly: compare sizes via first 8 bytes
            if US[b-0x08000000:b-0x08000000+4]==JP[cand-0x08000000:cand-0x08000000+4]:
                amap[b]=cand; added+=1
    print('round',rnd,'mapped',len(amap),'added',added)
pickle.dump(amap,open('/home/claude/work/amap.pkl','wb'))
names={s[0]:s[2] for s in named}
c=collections.Counter((a>>24) for a in amap)
print(c)
