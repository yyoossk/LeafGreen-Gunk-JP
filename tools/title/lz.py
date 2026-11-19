def decomp(d,o=0):
    assert d[o]==0x10; n=d[o+1]|d[o+2]<<8|d[o+3]<<16; i=o+4; out=bytearray()
    while len(out)<n:
        f=d[i]; i+=1
        for b in range(8):
            if len(out)>=n: break
            if f&(0x80>>b):
                x=d[i]<<8|d[i+1]; i+=2; ln=(x>>12)+3; disp=(x&0xFFF)+1
                for _ in range(ln): out.append(out[-disp])
            else: out.append(d[i]); i+=1
    return bytes(out), i-o
def comp(src):
    out=bytearray([0x10,len(src)&255,(len(src)>>8)&255,(len(src)>>16)&255]); i=0
    while i<len(src):
        fi=len(out); out.append(0); flag=0
        for b in range(8):
            if i>=len(src): break
            best=0;bd=0
            for disp in range(2,min(0x1000,i)+1):   # disp>=2: VRAM-safe
                l=0
                while l<18 and i+l<len(src) and src[i+l]==src[i-disp+l]: l+=1
                if l>best: best=l; bd=disp
                if best==18: break
            if best>=3:
                flag|=0x80>>b; x=((best-3)<<12)|(bd-1); out+=bytes([x>>8,x&255]); i+=best
            else: out.append(src[i]); i+=1
        out[fi]=flag
    while len(out)%4: out.append(0)
    return bytes(out)
