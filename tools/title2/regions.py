from PIL import Image, ImageDraw
W,H=256,160
REG={}  # name -> list of polygons (later ones override earlier)
ORDER=['leaf','pet','trk','eye','iris','mou','claw']
P={
 'leaf':[[(100,52),(220,52),(220,57),(100,57)],
         [(100,57),(135,57),(134,68),(100,69)],
         [(150,57),(171,57),(171,64),(165,71),(160,75),(157,74),(152,69),(150,63)],
         [(185,57),(220,57),(220,69),(189,68),(186,63)]],
 'pet':[[(100,14),(220,14),(220,51),(100,51)]],
 'trk':[[(158,36),(164,36),(168,39),(170,41),(170,51),(168,54),(166,56),(156,56),(153,54),(152,51),(152,40),(155,37)]],
 'eye':[[(140,72),(148,72),(148,79),(140,79)],[(172,72),(179,72),(179,78),(172,78)]],
 'iris':[],
 'mou':[],
 'claw':[],
}
def labels():
    lab=Image.new('L',(W,H),0)
    for i,n in enumerate(ORDER):
        for pts in P[n]:
            ImageDraw.Draw(lab).polygon(pts,fill=i+1)
    return lab
NAMES=['body']+ORDER

# 花びら: 輪郭(8,9)と背景で区切って塗りつぶし、その輪郭も花びらに含める。外れた所は葉っぱ
_labels_poly=labels
def labels():
    lab=_labels_poly(); L=lab.load()
    src=Image.open('render.png').load()
    PET=ORDER.index('pet')+1; LEAF=ORDER.index('leaf')+1; TRK=ORDER.index('trk')+1
    fill=set(); st=[(130,40),(180,40),(160,28),(140,30),(190,38)]
    for s in st:
        if src[s]>=10: fill.add(s)
    st=list(fill)
    while st:
        x,y=st.pop()
        for q in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if q in fill or not(0<=q[0]<W and 0<=q[1]<=51): continue
            if L[q]==TRK or src[q]<10: continue
            fill.add(q); st.append(q)
    edge=set()
    for (x,y) in fill:
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                q=(x+dx,y+dy)
                if q not in fill and src[q] in (6,7,8,9) and L[q]!=TRK: edge.add(q)
    for y in range(H):
        for x in range(W):
            if L[x,y]==PET: L[x,y]=PET if ((x,y) in fill or (x,y) in edge or y<44) else LEAF
    return lab
