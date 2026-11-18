import sys
r=bytearray(open(sys.argv[1],'rb').read()); p=open(sys.argv[2],'rb').read(); i=5
while p[i:i+3]!=b'EOF':
    o=int.from_bytes(p[i:i+3],'big'); L=int.from_bytes(p[i+3:i+5],'big'); i+=5
    if L==0: L=int.from_bytes(p[i:i+2],'big'); v=p[i+2]; i+=3; d=bytes([v])*L
    else: d=p[i:i+L]; i+=L
    r[o:o+len(d)]=d
open(sys.argv[3],'wb').write(r)
