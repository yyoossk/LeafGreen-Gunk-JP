import subprocess,sys,os
P='/home/claude/port'
os.makedirs(P+'/gx/o',exist_ok=True)
for f in os.listdir(P+'/gx/o'): os.remove(P+'/gx/o/'+f)
repl=[]
for line in open(P+'/gx/features.cfg'):
    line=line.split('#')[0].split()
    if not line: continue
    src,funcs=line[0],line[1:]
    base=os.path.basename(src)[:-2]
    out=f'{P}/gx/{base}.s'
    r=subprocess.run(['python3','/home/claude/tools/extract.py',src,out,','.join(funcs),'--auto-new'],capture_output=True,text=True)
    print(src, r.stdout.strip().replace('\n',' | ')); 
    if r.returncode: print(r.stderr); sys.exit(1)
    subprocess.check_call(['arm-none-eabi-as','-mcpu=arm7tdmi','-o',f'{P}/gx/o/{base}.o',out])
    for fn in funcs: repl.append((base+'.o',fn))
open(P+'/gx/replace.txt','w').write('\n'.join(f'{a} {b}' for a,b in repl)+'\n')
