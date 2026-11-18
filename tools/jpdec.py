import re,sys
def table():
    dec={}
    for line in open('/home/claude/port/charmap.txt',encoding='utf-8'):
        m=re.match(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$",line.split('@')[0].strip())
        if m:
            c,v=m.group(1),int(m.group(2),16)
            if '぀'<=c<='ヿ' or c in 'ー！？。、…・「」『』　' : dec[v]=c
            dec.setdefault(v,c)
    return dec
D=table()
def decode(b):
    out=''
    i=0
    while i<len(b):
        x=b[i]
        if x==0xFF: break
        if x==0xFE: out+='\\n'
        elif x==0xFA: out+='\\l'
        elif x==0xFB: out+='\\p'
        elif x==0xFD: out+='{V%d}'%b[i+1]; i+=1
        elif x==0xFC: out+='{FC%02x}'%b[i+1]; i+=1
        else: out+=D.get(x,'[%02x]'%x)
        i+=1
    return out
if __name__=='__main__':
    r=open('/home/claude/roms/Pocket Monsters - LeafGreen (Japan) (Rev 1).gba','rb').read()
    a=int(sys.argv[1],16)&0x1ffffff
    print(decode(r[a:a+300]))
