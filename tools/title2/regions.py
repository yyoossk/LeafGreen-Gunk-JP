from PIL import Image, ImageDraw
W,H=256,160
REG={}  # name -> list of polygons (later ones override earlier)
ORDER=['leaf','pet','trk','eye','iris','mou','claw']
P={
 'leaf':[[(100,36),(220,36),(220,72),(196,70),(190,64),(176,62),(168,60),(164,74),(156,74),(150,62),(140,62),(128,66),(124,72),(100,72)]],
 'pet':[[(110,18),(212,18),(212,44),(202,47),(196,50),(182,50),(172,48),(168,40),(166,32),(152,32),(150,47),(130,47),(120,44),(110,42)]],
 'trk':[[(153,32),(167,32),(169,40),(171,53),(149,53),(151,40)]],
 'eye':[[(140,72),(148,72),(148,79),(140,79)],[(172,72),(179,72),(179,78),(172,78)]],
 'iris':[],
 'mou':[[(152,91),(167,91),(167,93),(152,93)]],
 'claw':[],
}
def labels():
    lab=Image.new('L',(W,H),0)
    for i,n in enumerate(ORDER):
        for pts in P[n]:
            ImageDraw.Draw(lab).polygon(pts,fill=i+1)
    return lab
NAMES=['body']+ORDER
