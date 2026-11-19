import struct
from PIL import Image
from regions import *
src=Image.open('render.png').load(); lab=labels().load()
def ramp(*c): return dict(zip(range(8,16),c))
R={
'body':ramp((24,64,72),(36,88,96),(48,112,120),(64,140,144),(84,164,164),(108,188,184),(144,212,204),(188,236,228)),
'leaf':ramp((20,60,28),(30,84,36),(42,108,44),(58,134,56),(80,160,70),(110,184,88),(148,208,112),(190,230,150)),
'pet':ramp((110,30,56),(150,44,76),(190,64,96),(220,92,120),(240,124,148),(248,156,172),(252,192,204),(255,224,230)),
'trk':ramp((60,36,24),(84,54,32),(108,72,42),(134,92,54),(160,114,68),(184,138,86),(206,164,110),(228,192,140)),
}
WHITE=(248,248,248); IRIS=(200,40,40); MOUTH={8:(80,20,30),9:(120,32,48),10:(150,44,62),11:(176,60,80)}
CLAW={14:(224,224,212),15:(255,255,248)}
def g5(c): return tuple((v>>3)<<3 for v in c)
def color(x,y):
    s=src[x,y]
    if s in (0,2): return None
    n=NAMES[lab[x,y]]
    if s<8: s=8
    if n=='eye':
        if s>=14: return WHITE
        if s==8: return IRIS
        n='body'
    if n=='mou': return MOUTH.get(s,MOUTH[11])
    if n=='body' and s>=14 and y>=88: return CLAW[s]
    return R[n][s]
img=[[None]*256 for _ in range(160)]
for y in range(160):
    for x in range(256):
        c=color(x,y); img[y][x]=g5(c) if c else None
# preview
pv=Image.open('render.png').convert('RGB'); p=pv.load()
for y in range(160):
    for x in range(256):
        if img[y][x]: p[x,y]=img[y][x]
pv.save('preview.png')
# tiles
ent=struct.unpack('<640H',open('map.bin','rb').read())
cells=[k for k,e in enumerate(ent) if e&0x3FF]
sets={}
for k in cells:
    cx,cy=k%32*8,k//32*8
    sets[k]=set(img[cy+j][cx+i] for j in range(8) for i in range(8) if img[cy+j][cx+i])
import random
def pack(order):
    pals=[]; assign={}; err=0
    for k in order:
        best=None
        for i,pl in enumerate(pals):
            u=len(pl|sets[k])
            if u<=15 and (best is None or u<best[0]): best=(u,i)
        if best: pals[best[1]]|=sets[k]; assign[k]=best[1]
        elif len(pals)<4: pals.append(set(sets[k])); assign[k]=len(pals)-1
        else:
            i=min(range(len(pals)),key=lambda i:len(pals[i]|sets[k])); assign[k]=i; err+=1
    return err,pals,assign
rng=random.Random(1); bestr=None
for t in range(3000):
    order=sorted(cells,key=lambda k:-len(sets[k])) if t==0 else rng.sample(cells,len(cells))
    r=pack(order)
    if bestr is None or r[0]<bestr[0]: bestr=r
    if r[0]==0: break
err,pals,assign=bestr
print('palettes',[len(p) for p in pals],'overflow tiles',err, 'max set',max(len(s) for s in sets.values()))
# ---- emit
import sys; sys.path.insert(0,'.')
from lz import comp, decomp
PBASE=10
pl=[[None]+sorted(p) for p in pals]
while len(pl)<4: pl.append([None])
for p in pl:
    while len(p)<16: p.append((0,0,0))
tiles=bytearray(open('tiles.bin','rb').read())
newmap=list(ent); used={}; ntiles=len(tiles)//32
for k in cells:
    pi=assign[k]; P=pl[pi]
    def idx(c):
        if c is None: return 0
        if c in P: return P.index(c)
        return min(range(1,16),key=lambda i:sum((a-b)**2 for a,b in zip(P[i],c)))
    t=bytearray(32)
    cx,cy=k%32*8,k//32*8
    for j in range(8):
        for i in range(0,8,2):
            t[j*4+i//2]=idx(img[cy+j][cx+i])|(idx(img[cy+j][cx+i+1])<<4)
    tn=ent[k]&0x3FF
    if tn in used and used[tn]!=bytes(t):
        tn=ntiles; ntiles+=1; tiles+=bytes(32)
    used[tn]=bytes(t); tiles[tn*32:tn*32+32]=t
    newmap[k]=tn|((PBASE+pi)<<12)
for k in range(640):
    if not ent[k]&0x3FF: newmap[k]=ent[k]
pal=b''.join(struct.pack('<H',(r>>3)|((g>>3)<<5)|((b>>3)<<10)) for p in pl for (r,g,b) in [(c if c else (0xF0,0x90,0x60)) for c in p])
open('title_pals.bin','wb').write(pal)
open('title_mon.4bpp.lz','wb').write(comp(bytes(tiles)))
mb=struct.pack('<640H',*newmap)
open('title_map.bin.lz','wb').write(comp(mb))
assert decomp(open('title_mon.4bpp.lz','rb').read())[0]==bytes(tiles)
print('tiles',ntiles,'sizes',len(comp(bytes(tiles))),len(comp(mb)))
