import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
from PIL import Image
g=Game('jp','/tmp/t16/n.ss',rom=sys.argv[1]); g.run(10)
for f in list(range(0x820,0x828))+list(range(0x890,0x89A)): g.setflag(f)
g.teleport('ROCK_TUNNEL_1F',17,4); g.run(200)
g.tap('S'); g.run(40)
for i in range(4): g.cmd('tap D 1'); g.run(6)
g.tap('A'); g.run(150)
fs=[]
for k,key in enumerate(['R','R','D','D','D','D','D','D','D','A']):
    g.tap(key); g.run(40); fn=f'/tmp/t16/nav{k}.png'; g.shot(fn); fs.append(fn)
g.run(400); g.shot('/tmp/t16/navend.png'); print('pos',g.pos()); g.close()
W=Image.new('RGB',(240*5,320))
for i,f in enumerate(fs): W.paste(Image.open(f),((i%5)*240,(i//5)*160))
W.save('/tmp/t16/nav.png')
