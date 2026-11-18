import pickle,re,collections
amap=pickle.load(open('/home/claude/work/amap.pkl','rb'))
# parse map: file -> name->addr
cur=None; filesyms=collections.defaultdict(dict); glob={}
for line in open('/home/claude/pret/pokeleafgreen_rev1.map'):
    m=re.match(r'\s*\.?\w*\s+0x([0-9a-f]{8,16})\s+0x[0-9a-f]+\s+(\S+\.o)',line)
    if m: cur=m.group(2).split('/')[-1]; continue
    m=re.match(r'\s+0x([0-9a-f]{8,16})\s+([A-Za-z_]\w*)\s*$',line)
    if m and cur:
        filesyms[cur][m.group(2)]=int(m.group(1),16)
nm={}
dup=collections.Counter()
for line in open('/home/claude/work/us.nm'):
    p=line.split()
    if len(p)==3:
        a,t,n=int(p[0],16),p[1],p[2]
        if t in 'TDBR' or t in 'tdbr':
            if n in nm and nm[n]!=a: dup[n]+=1
            nm.setdefault(n,a)
def us(name,file=None):
    if file and name in filesyms.get(file,{}): return filesyms[file][name]
    return nm.get(name)
def jp(name,file=None):
    a=us(name,file)
    if a is None: return None,None
    return a, amap.get(a)
import pickle as _p
_fm=_p.load(open('/home/claude/work/fmatch.pkl','rb'))
def ident(name,file=None):
    a=us(name,file)
    if a is None: return None
    r=_fm.get(a&~1)
    return bool(r and r[1])
