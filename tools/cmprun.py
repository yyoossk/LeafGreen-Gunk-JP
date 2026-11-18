import sys,subprocess,struct,os
sys.path.insert(0,'/home/claude/tools')
import mkmon
ROMS={'en':dict(rom='/home/claude/gunk/pokefirered_release.gba',party=0x02024284,cnt=0x02024029,obj=0x02036E50,rng=0x03005000,sb1=0x03005008),
      'jp':dict(rom='/home/claude/work/port.gba',party=0x020241E4,cnt=0x02023F89,obj=0x02036D6C,rng=0x03004FA0,sb1=0x03004FA8)}
def run(rom,cmds):
    r=subprocess.run(['/home/claude/emu/gbarun',rom,'-'],input='\n'.join(cmds)+'\n',capture_output=True,text=True)
    return [bytes(int(x,16) for x in l.split(':')[1].split()) for l in r.stdout.splitlines() if ':' in l]
def ptrs(k,state):
    R=ROMS[k]
    sb1,sb2=[struct.unpack('<I',b)[0] for b in run(R['rom'],['ls '+state,f'peek {R["sb1"]:08X} 4',f'peek {R["sb1"]+4:08X} 4'])]
    key=struct.unpack('<H',run(R['rom'],['ls '+state,f'peek {sb2+0xF20:08X} 2'])[0])[0]
    return sb1,sb2,key
POCKET={'items':0x310,'key':0x3B8,'balls':0x430,'tm':0x464,'berries':0x54C,'med':0x348C,'held':0x352C}
def build(scn,k,states,tag):
    R=ROMS[k]; out=[]; P=None
    for line in scn.splitlines():
        p=line.split()
        if not p: continue
        if p[0]=='STATE': out.append('ls '+states[k])
        elif p[0]=='MON':  # MON slot species move1 move2 move3 move4
            slot=int(p[1]); sp=int(p[2]); mv=tuple(int(x) for x in p[3:7]); lv=int(p[7]) if len(p)>7 else 5
            data=mkmon.mon(sp,level=lv,moves=mv,pid=0x1000+slot)
            base=R['party']+100*slot
            out+=[f'poke {base+i:08X} {b:02X}' for i,b in enumerate(data)]
        elif p[0]=='EGG':  # EGG slot species
            slot=int(p[1]); d=mkmon.mon(int(p[2]),level=5,nick='タマゴ',pid=0x3000+slot,egg=True)
            base=R['party']+100*slot
            out+=[f'poke {base+i:08X} {b:02X}' for i,b in enumerate(d)]
        elif p[0]=='COUNT': out.append(f'poke {R["cnt"]:08X} {int(p[1]):02X}')
        elif p[0]=='SEED':
            v=int(p[1],16); out+=[f'poke {R["rng"]+i:08X} {(v>>(8*i))&0xFF:02X}' for i in range(4)]
        elif p[0]=='FLAG':
            f=int(p[1],16); out.append(f'orptr {R["sb1"]:08X} {0xEE0+f//8:X} {1<<(f%8):X}')
        elif p[0]=='BAG':  # BAG pocket slot item qty  (only valid right after STATE)
            if P is None: P=ptrs(k,states[k])
            sb1,sb2,key=P; a=sb1+POCKET[p[1]]+4*int(p[2]); it=int(p[3]); q=int(p[4])^key
            out+=[f'poke {a+i:08X} {b:02X}' for i,b in enumerate(struct.pack('<HH',it,q))]
        elif p[0]=='MONEY':  # MONEY amount (only valid right after STATE)
            if P is None: P=ptrs(k,states[k])
            sb1,sb2,key=P; v=int(p[1])^(key|(key<<16)) if False else int(p[1])
            kk=struct.unpack('<I',run(R['rom'],['ls '+states[k],f'peek {sb2+0xF20:08X} 4'])[0])[0]
            out+=[f'poke {sb1+0x290+i:08X} {b:02X}' for i,b in enumerate(struct.pack('<I',int(p[1])^kk))]
        elif p[0]=='VAR':  # VAR 0x40xx value
            v=int(p[1],16)-0x4000; val=int(p[2],0)
            out+=[f'pokeptr {R["sb1"]:08X} {0x1000+2*v+i:X} {(val>>(8*i))&0xFF:X}' for i in range(2)]
        elif p[0]=='SB1':  # SB1 hexoff byte byte ...
            o=int(p[1],16); out+=[f'pokeptr {R["sb1"]:08X} {o+i:X} {int(x,16):X}' for i,x in enumerate(p[2:])]
        elif p[0]=='LOG': out.append(f'peek {R["obj"]:08X} 576')
        elif p[0]=='SHOT': out.append(f'shot /tmp/cmp_{tag}_{p[1]}_{k}.png')
        elif p[0]=='SAVE': out.append(f'ss /tmp/cmpst_{p[1]}_{k}.ss')
        else: out.append(line)
    r=subprocess.run(['/home/claude/emu/gbarun',R['rom'],'-'],input='\n'.join(out)+'\n',capture_output=True,text=True)
    logs=[]
    for line in r.stdout.splitlines():
        if ':' not in line: continue
        b=bytes(int(x,16) for x in line.split(':')[1].split())
        if len(b)<576:
            logs.append(b.hex()); continue
        s=[]
        for i in range(16):
            o=b[i*36:(i+1)*36]
            if o[0]&1 and o[8] in (254,255): s.append(('P' if o[8]==255 else 'F')+str(struct.unpack_from('<hh',o,0x10))+('i' if o[1]&0x20 else ''))
        logs.append(' '.join(sorted(s)))
    return logs
if __name__=='__main__':
    scn=open(sys.argv[1]).read(); tag=os.path.basename(sys.argv[1]).split('.')[0].replace('_','-')
    states={'en':sys.argv[2],'jp':sys.argv[3]}
    le=build(scn,'en',states,tag); lj=build(scn,'jp',states,tag)
    bad=0
    for i,(a,b) in enumerate(zip(le,lj)):
        m='  ' if a==b else '!!'; bad+=a!=b
        print(f'{m} {i:2d} EN {a:40s} JP {b}')
    print('MISMATCH' if bad or len(le)!=len(lj) else 'ALL SAME', len(le), len(lj))
    # side by side shots
    from PIL import Image
    shots=sorted(set(f.split('_')[2] for f in os.listdir('/tmp') if f.startswith(f'cmp_{tag}_')))
    if shots:
        W=Image.new('RGB',(480,160*len(shots)))
        for i,s in enumerate(shots):
            for j,k in enumerate(('en','jp')):
                fn=f'/tmp/cmp_{tag}_{s}_{k}.png'
                if os.path.exists(fn): W.paste(Image.open(fn),(240*j,160*i))
        W.save(f'/tmp/cmp_{tag}.png')
