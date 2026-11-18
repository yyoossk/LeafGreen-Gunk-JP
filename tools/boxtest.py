# 16-box test: make a vanilla JP save with boxed Pokémon, load it with the port, check the conversion
import sys,subprocess,struct,os
sys.path.insert(0,'/home/claude/tools'); import mkmon
VAN='/home/claude/roms/Pocket Monsters - LeafGreen (Japan) (Rev 1).gba'; PORT='/home/claude/work/port.gba'
SAV='/home/claude/work/boxtest/v.sav'
def run(rom,cmds,sav=SAV):
    r=subprocess.run(['/home/claude/emu/gbarun',rom,'-',sav],input='\n'.join(cmds)+'\n',capture_output=True,text=True)
    return [bytes(int(x,16) for x in l.split(':')[1].split()) for l in r.stdout.splitlines() if ':' in l and not l.startswith('frame')]
NEWGAME=["run 900","tap A 3","run 200","tap A 96","tap A 72","tap A 48","run 300","tap A 6","tap B 6","run 60","hold R 80","hold U 80","hold L 20","run 200","hold L 50","run 20","hold L 32","hold D 120","run 200","shot /home/claude/work/boxtest/a_out.png"]
BOXED={(0,0):(25,(85,0,0,0)),(0,1):(1,(354,300,1,2)),(6,15):(150,(94,0,0,0)),(13,29):(151,(1,0,0,0))}
def phaseA():
    if os.path.exists(SAV): os.remove(SAV)
    c=list(NEWGAME)
    party=0x020241E4
    for slot,(sp,mv) in enumerate([(63,(100,0,0,0)),(4,(10,45,52,0))]):
        d=mkmon.mon(sp,level=20,moves=mv,pid=0x1000+slot)
        c+=[f'poke {party+100*slot+i:08X} {b:02X}' for i,b in enumerate(d)]
    c+=['poke 02023F89 02',f'orptr 03004FA8 {0xEE0+0x828//8:X} {1<<(0x828%8):X}']
    for i,b in enumerate(bytes([3,1,0xFF,0,26,0,27,0])): c.append(f'pokeptr 03004FA8 {0x1C+i:X} {b:X}')
    for (bx,sl),(sp,mv) in BOXED.items():
        d=mkmon.mon(sp,level=50,moves=mv,pid=0x2000+bx*30+sl,nick='テスト')[:80]
        o=4+(bx*30+sl)*80
        c+=[f'pokeptr 03004FB0 {o+i:X} {b:X}' for i,b in enumerate(d)]
    c+=['tap S','run 20','tap D','tap D','tap D','tap A','run 200','tap A','run 2500','tap A','run 200','shot /home/claude/work/boxtest/a_saved.png','ss /home/claude/work/boxtest/a.ss']
    run(VAN,c)
CONT=["ls /home/claude/work/boxtest/a.ss","reset","run 900","tap A 3","run 200","tap A","run 120","tap A","run 400","shot /home/claude/work/boxtest/b_cont.png"]
def phaseB():
    c=list(CONT)+['peek 03004FB0 4']
    p=struct.unpack('<I',run(PORT,c)[0])[0]
    raw=run(PORT,list(CONT)+[f'peek {p:08X} {0x83D0}'])[0]
    return raw
def unpack(src):
    box=bytearray(80); box[0:18]=src[0:18]; box[19:28]=src[18:27]
    lo,hi=struct.unpack_from('<II',src,61); box[18]=(hi>>29)&7
    return box,lo,hi
if __name__=='__main__':
    phaseA(); raw=phaseB()
    print('format',raw[0x83CC:0x83D0])
    for (bx,sl),(sp,mv) in BOXED.items():
        o=4+(bx*30+sl)*69; box,lo,hi=unpack(raw[o:o+69])
        print(bx,sl,'species',lo&0x3FF,'item',(lo>>10)&0x3FF,'moves',(lo>>20)&0x3FF,(lo>>30)|((hi&0xFF)<<2),(hi>>8)&0x3FF,(hi>>18)&0x3FF,'lang',box[18],'bad',(hi>>28)&1,'pid',hex(struct.unpack_from('<I',box,0)[0]))
    names=raw[0x8164:0x8164+16*9]
    print('names',[names[i*9:i*9+9].hex() for i in (0,13,14,15)])
    print('wall',list(raw[0x81F4:0x8204]))
    # count non-empty packed slots
    n=sum(1 for i in range(16*30) if any(raw[4+i*69:4+i*69+69]))
    print('nonempty',n)
