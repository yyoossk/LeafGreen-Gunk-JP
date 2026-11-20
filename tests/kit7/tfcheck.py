import sys,json,struct,os; sys.path.insert(0,'/home/claude/tools'); from walker import *
import walker
from PIL import Image
P='/home/claude/pret';F='/home/claude/frlgplus'
maps=json.load(open(P+'/data/maps/map_groups.json'))
lay_of={}
for grp in maps['group_order']:
    for m in maps[grp]:
        j=json.load(open(f'{P}/data/maps/{m}/map.json')); lay_of.setdefault(j['layout'],[]).append(j['id'])
L={l['id']:l for l in json.load(open(P+'/data/layouts/layouts.json'))['layouts'] if 'blockdata_filepath' in l}
todo=['CeladonCity','CeruleanCave_B1F','CeruleanCity','CinnabarIsland','FiveIsland_ResortGorgeous_House','FourIsland_IcefallCave_1F','Route14','Route20','Route25','Route8','SilphCo_1F','SilphCo_3F','ViridianCity','ViridianForest']
jobs=[]
for name in todo:
    lid=[k for k,v in L.items() if v['blockdata_filepath'].split('/')[2]==name][0]; w=L[lid]['width']
    a=open(f'{P}/data/layouts/{name}/map.bin','rb').read(); b=open(f'{F}/data/layouts/{name}/map.bin','rb').read()
    cells=[k for k in range(len(a)//2) if a[2*k:2*k+2]!=b[2*k:2*k+2]]
    xs=[k%w for k in cells]; ys=[k//w for k in cells]
    mid=(sorted(xs)[len(xs)//2],sorted(ys)[len(ys)//2])
    mapid=lay_of[lid][0].replace('MAP_','')
    jobs.append((name,mapid,mid))
print(jobs)
for tag,rom,st in (('o','/home/claude/roms/Pocket Monsters - LeafGreen (Japan) (Rev 1).gba','/tmp/t7/van.ss'),('p','/home/claude/work/port.gba','/tmp/t7/pat2.ss')):
    g=Game('jp',st,rom=rom); g.run(10)
    for i,(n,m,(x,y)) in enumerate(jobs):
        try: g.teleport(m,x,y); g.run(90); g.shot(f'/tmp/t7/tf_{tag}{i}.png')
        except Exception as e: print('ERR',m,e)
    g.close()
W=Image.new('RGB',(488,160*len(jobs)),(255,255,255))
for i in range(len(jobs)):
    for j,tag in enumerate('op'):
        f=f'/tmp/t7/tf_{tag}{i}.png'
        if os.path.exists(f): W.paste(Image.open(f).convert('RGB'),(248*j,160*i))
W.save('/tmp/t7/tf.png')
