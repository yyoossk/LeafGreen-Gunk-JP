import sys,subprocess,re,difflib,syms
US=open('/home/claude/pret/pokeleafgreen_rev1.gba','rb').read()
JP=open('/home/claude/roms/Pocket Monsters - LeafGreen (Japan) (Rev 1).gba','rb').read()
def size_us(name):
    out=subprocess.check_output(['arm-none-eabi-nm','-S','/home/claude/pret/pokeleafgreen_rev1.elf']).decode()
    for l in out.splitlines():
        p=l.split()
        if len(p)==4 and p[3]==name: return int(p[1],16)
def dis(rom,a,n):
    open('/tmp/fd.bin','wb').write(rom[a&0x1ffffff:(a&0x1ffffff)+n])
    o=subprocess.run(['arm-none-eabi-objdump','-D','-bbinary','-marm','-Mforce-thumb','/tmp/fd.bin'],capture_output=True,text=True).stdout.split('<.data>:')[1]
    ins=[]
    for l in o.splitlines():
        p=l.split('\t')
        if len(p)>=3:
            t=p[2]+' '+(p[3] if len(p)>3 else '')
            t=re.sub(r'0x[0-9a-f]+','X',t); t=re.sub(r'@.*','',t)
            ins.append(t.strip())
    return ins
name=sys.argv[1]; f=sys.argv[2] if len(sys.argv)>2 else 'item_menu.o'
u,j=syms.jp(name,f); n=size_us(name)
a=dis(US,u,n); b=dis(JP,j,n+0x40)
sm=difflib.SequenceMatcher(None,a,b[:len(a)+16])
for op,i1,i2,j1,j2 in sm.get_opcodes():
    if op!='equal': print(op, a[i1:i2][:6], '|', b[j1:j2][:6])
