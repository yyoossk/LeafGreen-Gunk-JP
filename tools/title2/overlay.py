import sys
from PIL import Image, ImageDraw
from regions import *
im=Image.open('render.png'); src=im.load()
lab=labels().load()
col={'body':(60,160,170),'leaf':(40,140,50),'pet':(240,110,150),'trk':(150,100,60),'eye':(255,255,255),'iris':(220,40,40),'mou':(150,30,60),'claw':(255,255,180)}
rgb=im.convert('RGB'); o=rgb.load()
for y in range(H):
  for x in range(W):
    if src[x,y]==0: continue
    c=col[NAMES[lab[x,y]]]; s=(src[x,y]-6)/9
    o[x,y]=tuple(int(c[i]*(0.35+0.85*s)) if True else 0 for i in range(3))
import os; x0,y0,x1,y1=[int(v) for v in os.environ.get("BOX","100,14,220,110").split(",")]; S=int(os.environ.get("S","6"))
c=rgb.crop((x0,y0,x1,y1)).resize(((x1-x0)*S,(y1-y0)*S),Image.NEAREST); d=ImageDraw.Draw(c)
for x in range(x0,x1,8): d.line([((x-x0)*S,0),((x-x0)*S,c.size[1])],fill=(255,255,0)); d.text(((x-x0)*S+1,0),str(x),fill=(0,0,0))
for y in range(y0,y1,8): d.line([(0,(y-y0)*S),(c.size[0],(y-y0)*S)],fill=(255,255,0)); d.text((1,(y-y0)*S+1),str(y),fill=(0,0,0))
c.save(sys.argv[1] if len(sys.argv)>1 else '/tmp/ov.png')
