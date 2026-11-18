import struct,sys
def mon(species=4,level=5,nick='ヒトカゲ',pid=0,otid=0x12345678,moves=(10,45,0,0),friendship=70,shiny=False,egg=False):
    import re
    jp={}
    for line in open('/home/claude/port/charmap.txt',encoding='utf-8'):
        m=re.match(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})",line)
        if m: jp[m.group(1)]=int(m.group(2),16)
    nb=bytes(jp[c] for c in nick)+b'\xff'*10; nb=nb[:10]
    ot=bytes(jp[c] for c in 'あああああ')+b'\xff'*7; ot=ot[:7]
    n=level; exp=max(0,int(6*n**3/5-15*n*n+100*n-140)) if n>1 else 0
    if egg: friendship=0
    G=struct.pack('<HHIBBH',species,0,exp,0,friendship,0)
    A=struct.pack('<4H4B',*moves,*[(20 if m else 0) for m in moves])
    E=bytes([252,252,6,0,0,0])+bytes(6)
    ivs=(31|31<<5|31<<10|31<<15|31<<20|31<<25)
    if egg: ivs|=1<<30; friendship=0
    M=struct.pack('<BBHII',0,0x58,(level)|(4<<7)|(4<<11),ivs,0)
    order=['GAEM','GAME','GEAM','GEMA','GMAE','GMEA','AGEM','AGME','AEGM','AEMG','AMGE','AMEG','EGAM','EGMA','EAGM','EAMG','EMGA','EMAG','MGAE','MGEA','MAGE','MAEG','MEGA','MEAG'][pid%24]
    sub={'G':G,'A':A,'E':E,'M':M}
    dec=b''.join(sub[c] for c in order)
    ck=sum(struct.unpack('<24H',dec))&0xFFFF
    key=pid^otid
    enc=b''.join(struct.pack('<I',struct.unpack_from('<I',dec,i)[0]^key) for i in range(0,48,4))
    box=struct.pack('<II',pid,otid)+nb+bytes([1,0x06 if egg else 0x02])+ot+bytes([0])+struct.pack('<HH',ck,0)+enc
    assert len(box)==80
    hp=20 if level<50 else 999
    st=(11,10,12,11,10) if level<50 else (999,999,999,999,999)
    party=box+struct.pack('<IBBHH5H',0,level,0xFF,hp,hp,*st)
    assert len(party)==100
    return party
if __name__=='__main__':
    sp=int(sys.argv[1]) if len(sys.argv)>1 else 4
    p=mon(sp)
    base=int(sys.argv[2],16) if len(sys.argv)>2 else 0x020241E4
    cnt=sys.argv[3] if len(sys.argv)>3 else "02023F89"
    for i,b in enumerate(p): print(f'poke {base+i:08X} {b:02X}')
    print("poke "+cnt+" 01")
