import sys
final=open(sys.argv[1],'rb').read(); bases=[open(p,'rb').read() for p in sys.argv[3:]]
n=len(final); assert all(len(b)==n for b in bases)
diff=bytearray(n)
for b in bases:
    for i in range(n):
        pass
import numpy as np
f=np.frombuffer(final,dtype=np.uint8)
m=np.zeros(n,dtype=bool)
for b in bases: m|= (np.frombuffer(b,dtype=np.uint8)!=f)
idx=np.flatnonzero(m)
out=bytearray(b'PATCH')
# group into runs, merging gaps <6
runs=[]
s=e=None
for i in idx:
    if s is None: s=e=i
    elif i-e<=6: e=i
    else: runs.append((s,e)); s=e=i
if s is not None: runs.append((s,e))
runs=[(int(a),int(b)) for a,b in runs]
for s,e in runs:
    if s==0x454F46: s-=1
    p=s
    while p<=e:
        L=min(0xFFFF,e-p+1)
        if p==0x454F46: p-=1; L=min(0xFFFF,e-p+1)
        out+=p.to_bytes(3,'big')+L.to_bytes(2,'big')+final[p:p+L]; p+=L
out+=b'EOF'
open(sys.argv[2],'wb').write(out); print('records',len(runs),'size',len(out))
