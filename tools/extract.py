"""Compile a Gunk source file with statics made global, keep only chosen functions/objects.
usage: extract.py gunkfile.c out.s keep1,keep2,...  [--auto-new]
--auto-new also keeps objects referenced by kept chunks that do not exist in vanilla US."""
import sys,subprocess,re,os
sys.path.insert(0,'/home/claude/tools')
from syms import us, filesyms
G='/home/claude/gunk'
src=sys.argv[1]; out=sys.argv[2]; keep=set(x for x in sys.argv[3].split(',') if x)
auto='--auto-new' in sys.argv
base=os.path.basename(src)[:-2]
pp=subprocess.run(f"cc -E -iquote include -Wno-trigraphs -DLEAFGREEN -DREVISION=1 -DENGLISH -DMODERN=0 -DGUNK_TEST_HOOKS=0 -I tools/agbcc/include -I tools/agbcc -nostdinc -undef -std=gnu89 -Dstatic= {src} | tools/preproc/preproc -i {src} charmap.txt | tools/agbcc/bin/agbcc -mthumb-interwork -Wimplicit -Wparentheses -O2 -fhex-asm -o - -",shell=True,cwd=G,capture_output=True,text=True)
if pp.returncode: print(pp.stderr[-3000:]); sys.exit(1)
asm=pp.stdout.splitlines()
chunks=[]; cur=None; sect='.text'; pend=[]
for l in asm:
    s=l.strip()
    if s.startswith('.text') or s.startswith('.data') or s.startswith('.section') or s.startswith('.bss'):
        sect=s; pend=[]; continue
    m=re.match(r'^([A-Za-z_]\w*):',l)
    if m:
        cur={'name':m.group(1),'sect':sect,'lines':pend+[l]}; chunks.append(cur); pend=[]; continue
    if s.startswith('.globl') or s.startswith('.type') or s.startswith('.thumb_func') or s.startswith('.align') or s.startswith('.size'):
        if cur is None or s.startswith('.globl') or s.startswith('.type') or s.startswith('.thumb_func'):
            pend.append(l); continue
    if s.startswith('.comm') or s.startswith('.lcomm'):
        chunks.append({'name':s.split()[1].rstrip(','),'sect':'comm','lines':[l]}); continue
    if cur is not None: cur['lines'].append(l)
    else: pend.append(l)
byname={c['name']:c for c in chunks}
defined=set(byname)
def refs(c):
    r=set()
    for l in c['lines']:
        for w in re.findall(r'\b([A-Za-z_]\w*)\b',l.split('@')[0]):
            if w in defined: r.add(w)
    return r
GLOBALS=set()
for _l in open('/home/claude/work/us.nm'):
    _p=_l.split()
    if len(_p)==3 and _p[1] in 'TDRB': GLOBALS.add(_p[2])
_OBJ=set()
import subprocess as _sp, os as _os
_of='/home/claude/pret/build/leafgreen_rev1/src/'+base+'.o'
if _os.path.exists(_of):
    for _l in _sp.check_output(['arm-none-eabi-nm',_of]).decode().splitlines():
        _p=_l.split()
        if len(_p)==3: _OBJ.add(_p[2])
def exists_vanilla(n):
    return n in _OBJ or n in GLOBALS
kept=set(); todo=list(keep)
while todo:
    n=todo.pop()
    if n in kept: continue
    if n not in byname: print('NOTFOUND',n); continue
    kept.add(n)
    for r in refs(byname[n]):
        if r in kept: continue
        if r in keep: continue
        if auto and not exists_vanilla(r): todo.append(r)
outl=['.syntax divided','.thumb']
for c in chunks:
    if c['name'] in kept:
        sec=c['sect']
        outl.append(sec if not sec.startswith('.section') else sec)
        outl+=c['lines']
outl.append('.text\n.align 2, 0')
open(out,'w').write('\n'.join(outl)+'\n')
newobjs=[n for n in kept if not exists_vanilla(n)]
print('kept',sorted(kept)); print('new(not in vanilla)',sorted(newobjs))
