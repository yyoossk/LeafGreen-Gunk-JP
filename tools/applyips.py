import sys
r=bytearray(open(sys.argv[1],'rb').read()); p=open(sys.argv[2],'rb').read(); i=5
while p[i:i+3]!=b'EOF':
    o=int.from_bytes(p[i:i+3],'big'); L=int.from_bytes(p[i+3:i+5],'big'); i+=5
    if L==0: L2=int.from_bytes(p[i:i+2],'big'); r[o:o+L2]=p[i+2:i+3]*L2; i+=3
    else: r[o:o+L]=p[i:i+L]; i+=L
open(sys.argv[3],'wb').write(r)
