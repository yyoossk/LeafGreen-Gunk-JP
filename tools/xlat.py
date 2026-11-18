# JP FireRed (Rev1) address -> JP LeafGreen (Rev1) address, via US symbols
import pickle,bisect,collections
def loadnm(p):
    d={};dup=set()
    for line in open(p):
        s=line.split()
        if len(s)==3 and not s[2].startswith('.') and not s[2].startswith('$'):
            a=int(s[0],16)
            if s[2] in d and d[s[2]]!=a: dup.add(s[2])
            d.setdefault(s[2],a)
    for n in dup: d.pop(n,None)
    return d
FRN=loadnm('/home/claude/work_fr/us.nm'); LGN=loadnm('/home/claude/work/us.nm')
AF=pickle.load(open('/home/claude/work_fr/amap.pkl','rb')); AL=pickle.load(open('/home/claude/work/amap.pkl','rb'))
pairs={}
for n,uf in FRN.items():
    ul=LGN.get(n)
    if ul is None: continue
    jf=AF.get(uf); jl=AL.get(ul)
    if jf is None or jl is None: continue
    pairs.setdefault(jf,[]).append((jl,n))
P0=sorted((k,collections.Counter(j for j,_ in v).most_common(1)[0][0]) for k,v in pairs.items())
# drop outlier pairs: delta must agree with the majority of the 12 neighbours on each side
P=[]
for i,(k,v) in enumerate(P0):
    w=[b-a for a,b in P0[max(0,i-12):i+13]]
    c=collections.Counter(w).most_common(1)[0]
    if v-k==c[0] or w.count(v-k)>=4: P.append((k,v))
K=[p[0] for p in P]
def near(x):
    i=bisect.bisect_right(K,x)-1
    return P[i] if i>=0 else None
def fr2lg(x,check=True):
    lo=near(x); i=bisect.bisect_right(K,x)
    if lo is None: return None
    d=lo[1]-lo[0]
    return x+d
def info(x):
    i=bisect.bisect_right(K,x)-1
    out=[]
    for k in (i,i+1):
        if 0<=k<len(P): out.append((hex(P[k][0]),hex(P[k][1]),hex(P[k][1]-P[k][0]),pairs[P[k][0]][0][1]))
    return out
