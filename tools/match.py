import re, sys, pickle, struct
US=open('/home/claude/pret/pokeleafgreen_rev1.gba','rb').read()
JP=open('/home/claude/roms/Pocket Monsters - LeafGreen (Japan) (Rev 1).gba','rb').read()
syms=[]
for line in open('/home/claude/work/us.nm'):
    p=line.split()
    if len(p)<3: continue
    a=int(p[0],16); syms.append((a,p[1],p[2]))
rom=[s for s in syms if 0x08000000<=s[0]<0x09000000]
# function list with extents
addrs=sorted(set(s[0] for s in rom))
nexta={addrs[i]:addrs[i+1] for i in range(len(addrs)-1)}
funcs={}
for a,t,n in rom:
    if t in 'tT' and not n.startswith('.') and a<0x081EA000:
        funcs.setdefault(a&~1,n)
def isptr(w):
    return (w>>24) in (2,3,8,9) 
def mask(buf, base):
    # returns list of (byte or None)
    m=list(buf); n=len(buf)
    i=0
    while i+3<n:
        h1=buf[i]|buf[i+1]<<8; h2=buf[i+2]|buf[i+3]<<8
        if (h1&0xF800)==0xF000 and (h2&0xF800)==0xF800:
            m[i:i+4]=[None]*4; i+=4; continue
        i+=2
    for i in range((-base)%4, n-3, 4):
        w=struct.unpack_from('<I',buf,i)[0]
        if isptr(w): m[i:i+4]=[None]*4
    return m
JPCODE=JP[:0x240000]
res={}
items=sorted(funcs.items())
if __name__=="__main__":
  pass
for k,(a,n) in enumerate(items if __name__=="__main__" else []):
    end=nexta.get(a, a+4)
    # extend over non-function syms (local labels) until next function
    j=a
    while True:
        nx=nexta.get(j)
        if nx is None or nx>=0x081EA000 or nx in funcs: end=nx or end; break
        j=nx
    size=end-a
    if size<8 or size>0x4000: continue
    off=a-0x08000000
    buf=US[off:off+size]
    m=mask(buf,a)
    # longest literal run
    best=(0,0); s=None
    for i,v in enumerate(m+[None]):
        if v is None:
            if s is not None and i-s>best[1]-best[0]: best=(s,i)
            s=None
        elif s is None: s=i
    if best[1]-best[0]<6: continue
    lit=bytes(m[best[0]:best[1]])
    cands=[]; p=JPCODE.find(lit)
    while p!=-1 and len(cands)<50:
        st=p-best[0]
        if st>=0 and (st%4)==(off%4):
            ok=True
            jb=JP[st:st+size]
            if len(jb)==size:
                mj=mask(jb,st+0x08000000)
                if mj==m: cands.append(st)
        p=JPCODE.find(lit,p+1)
    if len(cands)==1: res[a]=(n,cands[0]+0x08000000,size)
    elif len(cands)>1: res[a]=(n,None,size)
if __name__=="__main__": pickle.dump(res,open('/home/claude/work/fmatch.pkl','wb'))
if __name__=="__main__":
    u=sum(1 for v in res.values() if v[1]); print('funcs',len(funcs),'unique',u,'ambig',len(res)-u)
