from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, math
W,H=1200,675
B='/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
def F(s): return ImageFont.truetype(B,s,index=0)
# background: deep green -> yellow green
bg=Image.new('RGB',(W,H))
px=bg.load()
for y in range(H):
    t=y/H
    c=(int(10+60*t),int(70+110*t),int(25+20*t))
    for x in range(W): px[x,y]=c
# leaf pattern
lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
random.seed(7)
for i in range(70):
    cx,cy=random.randint(0,W),random.randint(int(H*0.35),H+40); s=random.randint(25,70); a=random.uniform(0,math.pi)
    pts=[]
    for k in range(24):
        u=k/23*math.pi*2; r=s*(abs(math.sin(u/2)))
        x=math.cos(u)*s*0.5; y=math.sin(u)*s*0.22
        pts.append((cx+x*math.cos(a)-y*math.sin(a), cy+x*math.sin(a)+y*math.cos(a)))
    d.polygon(pts,fill=(170,230,90,random.randint(25,70)))
lay=lay.filter(ImageFilter.GaussianBlur(2)); bg.paste(lay,(0,0),lay)
d=ImageDraw.Draw(bg)
def txt(xy,s,f,fill,stroke=0,sc=(0,0,0)): d.text(xy,s,font=f,fill=fill,stroke_width=stroke,stroke_fill=sc)
txt((58,40),'ポケットモンスター',F(46),(255,255,255),5,(20,60,20))
txt((58,98),'リーフグリーン',F(46),(255,255,255),5,(20,60,20))
# gold 改良パッチ with gradient
f=F(110); s='改良パッチ'
mask=Image.new('L',(W,H)); ImageDraw.Draw(mask).text((52,150),s,font=f,fill=255)
gold=Image.new('RGB',(W,H)); gp=gold.load()
for y in range(150,300):
    t=(y-165)/115; t=min(max(t,0),1)
    c=(255,int(235-80*t),int(120-100*t))
    for x in range(40,640): gp[x,y]=c
sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text((52,150),s,font=f,fill=(40,30,0,255),stroke_width=9,stroke_fill=(60,40,0,255))
bg.paste(sh,(0,0),sh); bg.paste(gold,(0,0),mask)
# title screen
t=Image.open('/tmp/cap/title.png').convert('RGB').resize((336,224),Image.NEAREST)
d.rectangle((808,14,1160,254),fill=(240,200,60)); bg.paste(t,(816,22))
# thumbnails
th=[('/tmp/cap/fol1.png','連れ歩き'),('/tmp/cap/cut2.png','ひでんわざ'),('/tmp/bt/jp_013_desk.png','バトルタワー'),('/tmp/walk/jp_00028_b.png','マスタートレーナー'),('/tmp/cap/sum2.png','個体値・努力値'),('/tmp/t151/oy_3.png','151匹揃う版')]
for i,(p,l) in enumerate(th):
    x=26+i*193; y=306
    d.rectangle((x,y,x+187,y+127),fill=(240,200,60))
    bg.paste(Image.open(p).convert('RGB').resize((180,120),Image.NEAREST),(x+4,y+4))
    w=d.textlength(l,font=F(22)); txt((x+94-w/2,y+138),l,F(22),(255,255,255),3,(20,60,20))
txt((58,525),'連れ歩き・ひでんわざ・バトルタワー・マスタートレーナー・ジムリーダー再戦 ほか',F(28),(255,255,255),4,(20,60,20))
txt((58,585),'通常版　／　151匹揃う版',F(44),(255,230,110),5,(40,50,10))
bg.save('/tmp/blog/header.jpg',quality=90)
