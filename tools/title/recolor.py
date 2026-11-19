from PIL import Image, ImageDraw
src=Image.open('render.png')   # indexed 0..15, full 256x160
W,H=src.size
def poly(pts):
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).polygon(pts,fill=255); return m
PET=poly([(117,32),(150,22),(172,22),(206,29),(206,45),(192,46),(186,52),(171,52),(171,44),(150,44),(149,52),(139,51),(126,48),(117,42)])
TRK=poly([(156,44),(165,44),(168,48),(168,53),(165,57),(156,57),(153,53),(153,48)])
LEA=poly([(103,58),(116,51),(150,51),(150,56),(171,56),(171,51),(197,52),(218,60),(216,69),(201,69),(192,62),(176,58),(146,58),(132,62),(127,70),(116,71),(103,66)])
LEA2=poly([(147,44),(173,44),(173,58),(147,58)])
EYE=Image.new('L',(W,H),0); d=ImageDraw.Draw(EYE); d.ellipse((138,69,149,79),fill=255); d.ellipse((171,69,182,79),fill=255)
PAL=[(246,148,98),(16,40,40),
     (24,72,88),(40,112,128),(72,160,168),(128,208,200),
     (152,40,72),(224,80,104),(248,136,144),(255,206,200),
     (32,96,40),(72,160,56),(144,216,96),
     (112,72,32),(176,120,64),
     (232,56,48)]
def mapc(s,reg):
    if s<6: return 0
    if s==6: return 1
    if reg=='eye' and s>=13: return 15
    if reg=='pet': return {7:6,8:6,9:7,10:7,11:8,12:8}.get(s,9)
    if reg=='lea': return 10 if s<=9 else (11 if s<=12 else 12)
    if reg=='trk': return 13 if s<=10 else 14
    return {7:2,8:2,9:3,10:3,11:4,12:4}.get(s,5)
out=Image.new('P',(W,H)); flat=[]; [flat.extend(c) for c in PAL]; out.putpalette(flat)
for y in range(H):
    for x in range(W):
        s=src.getpixel((x,y))
        reg='body'
        if EYE.getpixel((x,y)): reg='eye'
        elif TRK.getpixel((x,y)): reg='trk'
        elif PET.getpixel((x,y)): reg='pet'
        elif LEA.getpixel((x,y)) or LEA2.getpixel((x,y)): reg='lea'
        out.putpixel((x,y),mapc(s,reg))
out.save('recolor.png')
out.convert('RGB').crop((96,16,232,112)).resize((136*4,96*4),Image.NEAREST).save('/tmp/recolor.png')

# ---- build the 4bpp tiles in the original tile order (map unchanged), palette 13
import struct
m=open('map.bin','rb').read(); ent=struct.unpack('<640H',m)
tiles=bytearray(open('tiles.bin','rb').read())
for k,e in enumerate(ent):
    tn=e&0x3FF
    if not tn: continue
    hf=(e>>10)&1; vf=(e>>11)&1
    for y in range(8):
        for x in range(8):
            v=out.getpixel(((k%32)*8+x,(k//32)*8+y))
            sx=7-x if hf else x; sy=7-y if vf else y
            o=tn*32+sy*4+sx//2
            tiles[o]=(tiles[o]&0x0F)|(v<<4) if sx&1 else (tiles[o]&0xF0)|v
open('title_mon.4bpp','wb').write(tiles)
pal=b''.join(struct.pack('<H',(r>>3)|((g>>3)<<5)|((b>>3)<<10)) for r,g,b in PAL)
open('title_mon.gbapal','wb').write(pal)
