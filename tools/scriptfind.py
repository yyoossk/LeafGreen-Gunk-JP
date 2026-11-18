import re,struct,sys
sys.path.insert(0,'/home/claude/tools')
from syms import us
US=open('/home/claude/pret/pokeleafgreen_rev1.gba','rb').read()
JP=open('/home/claude/roms/Pocket Monsters - LeafGreen (Japan) (Rev 1).gba','rb').read()
def find_loadword(textsym):
    a=us(textsym); pat=b'\x0f\x00'+struct.pack('<I',a)
    i=US.find(pat); assert i>=0 and US.find(pat,i+1)<0, textsym
    return i+0x08000000
def jp_equiv(usaddr,before=24,after=24):
    o=usaddr-0x08000000; blob=US[o-before:o+after]
    pat=b''; i=0
    while i<len(blob):
        if i+3<len(blob) and blob[i+3] in (8,9) and blob[i+2]<0x80 and i>=0:
            pat+=b'....'; i+=4
        else:
            pat+=re.escape(blob[i:i+1]); i+=1
    ms=[m.start() for m in re.finditer(pat,JP,re.S)]
    return [m+before+0x08000000 for m in ms]
if __name__=='__main__':
    for t in sys.argv[1:]:
        u=find_loadword(t); print(t,hex(u),[hex(x) for x in jp_equiv(u)])
