# blog screenshots: common setup (player サトシ, Lv60 Venusaur lead, badges, bag)
import sys, struct; sys.path.insert(0,'/home/claude/tools')
from t151 import *
import mkmon
NAMES={3:'フシギバナ',149:'カイリュー',248:'バンギラス',376:'メタグロス',89:'ベトベトン',1:'フシギダネ'}
def base(rom, state='/tmp/walkst/s04_parcel_jp.ss', party=((3,60,(76,188,75,235)),)):
    g=Game('jp',state,rom=rom); g.run(10)
    sb2=g.u32(0x03004FAC)
    poke(g, sb2, bytes([0x5B,0x64,0x5C,0xFF,0xFF,0xFF,0xFF,0xFF]))
    for f in range(0x820,0x828): setflag(g,f)
    setflag(g,0x828); setflag(g,0x829); setflag(g,0x82F)
    own=g.peek(0x020241E4,100); otid=struct.unpack_from('<I',own,4)[0]
    data=b''
    for i,(sp,lv,mv) in enumerate(party):
        m=bytearray(mkmon.mon(sp,level=lv,moves=mv,pid=0x203+25*24*i,otid=otid,nick=NAMES.get(sp,'ポケモン')))
        m[20:27]=bytes([0x5B,0x64,0x5C,0xFF,0xFF,0xFF,0xFF])
        data+=bytes(m)
    poke(g,0x020241E4,data); setcount(g,len(party))
    return g
def bag(g, pocket, items):
    POCKET={'items':0x310,'key':0x3B8,'balls':0x430,'tm':0x464,'berries':0x54C,'med':0x348C,'held':0x352C}
    sb=sb1(g); key=g.u16(g.u32(0x03004FAC)+0xF20)
    for i,(it,q) in enumerate(items):
        poke(g, sb+POCKET[pocket]+4*i, struct.pack('<HH',it,q^key))
