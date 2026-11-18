import struct
ORD=['GAEM','GAME','GEAM','GEMA','GMAE','GMEA','AGEM','AGME','AEGM','AEMG','AMGE','AMEG','EGAM','EGMA','EAGM','EAMG','EMGA','EMAG','MGAE','MGEA','MAGE','MAEG','MEGA','MEAG']
def decode(b):
    pid,ot=struct.unpack_from('<II',b,0); key=pid^ot
    dec=b''.join(struct.pack('<I',struct.unpack_from('<I',b,32+i)[0]^key) for i in range(0,48,4))
    o=ORD[pid%24]; G=dec[o.index('G')*12:][:12]; E=dec[o.index('E')*12:][:12]
    sp,item,exp=struct.unpack_from('<HHI',G); return dict(species=sp,exp=exp,level=b[84],hp=struct.unpack_from('<H',b,86)[0],evs=list(E[:6]))
