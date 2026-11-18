import struct
ROMP='/home/claude/roms/Pocket Monsters - LeafGreen (Japan) (Rev 1).gba'
r=open(ROMP,'rb').read()
MAPGROUPS=0x08311F50
def u32(a): return struct.unpack_from('<I',r,a&0x1FFFFFF)[0]
def header(group,num):
    g=u32(MAPGROUPS+4*group); return u32(g+4*num)
def info(group,num):
    h=header(group,num)
    lay,ev,scr,con=struct.unpack_from('<IIII',r,h&0x1FFFFFF)
    o,w,c,b,po,pw,pc,pb=struct.unpack_from('<BBBBxxxxIIII',r,ev&0x1FFFFFF)[:8] if False else (None,)*8
    cnt=struct.unpack_from('<BBBB',r,ev&0x1FFFFFF); ptrs=struct.unpack_from('<IIII',r,(ev&0x1FFFFFF)+4)
    return dict(header=h,layout=lay,events=ev,scripts=scr,counts=cnt,ptrs=ptrs)
def objects(group,num):
    i=info(group,num); n=i['counts'][0]; p=i['ptrs'][0]
    return [r[(p&0x1FFFFFF)+24*k:(p&0x1FFFFFF)+24*k+24] for k in range(n)]
if __name__=='__main__':
    import sys
    g,n=int(sys.argv[1]),int(sys.argv[2]); i=info(g,n)
    print({k:(hex(v) if isinstance(v,int) else [hex(x) for x in v]) for k,v in i.items()})
    for o in objects(g,n): print(o.hex())
    lay=i['layout']&0x1FFFFFF; print('layout',struct.unpack_from('<iiIIII',r,lay))
    s=i['scripts']&0x1FFFFFF; print('mapscripts',r[s:s+16].hex())
