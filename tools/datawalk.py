import pickle,struct,bisect,collections
from propagate2 import US,JP,named,saddr,owner,amap,votes
import propagate2 as P
def rd(b,o): return struct.unpack_from('<I',b,o-0x08000000)[0]
datasyms=[s for s in named if 0x08000000<=s[0]<0x09000000 and s[1] in 'dDrR']
nexts={named[i][0]:named[i+1][0] for i in range(len(named)-1)}
for rnd in range(6):
    dv=collections.defaultdict(collections.Counter)
    for a,t,n in datasyms:
        if a not in amap: continue
        j=amap[a]; end=nexts.get(a,a+4); sz=min(end-a,0x10000)
        if a%4!=j%4: continue
        for i in range((-a)%4, sz-3, 4):
            w=rd(US,a+i)
            if (w>>24) in (8,9) and w<0x09000000:
                if j+i+4-0x08000000>len(JP): break
                v=rd(JP,j+i)
                if (v>>24)!=(w>>24): continue
                o=owner(w&~1 if w&1 and w<0x081EA000 else w)
                if o is None: continue
                dv[o[0]][v-(w-o[0])]+=1
            elif (w>>24) in (2,3):
                v=rd(JP,j+i)
                if (v>>24)!=(w>>24): continue
                o=owner(w)
                if o: dv[o[0]][v-(w-o[0])]+=1
    added=0
    for u,c in dv.items():
        if u in amap: continue
        (jv,cnt),=c.most_common(1)
        if cnt*2>sum(c.values()):
            amap[u]=jv; added+=1
    print('data round',rnd,'added',added,'total',len(amap))
    if not added: break
pickle.dump(amap,open('/home/claude/work/amap.pkl','wb'))
