import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
from PIL import Image
g=Game('jp',sys.argv[2],rom=sys.argv[1]); g.run(30)
S=[]
def sh(n): g.shot(f'/tmp/t2/lr{n}.png'); S.append(n)
g.tap('l'); g.run(90); sh(1)
g.tap('B'); g.run(120); sh(2)
g.tap('r'); g.run(90); sh(3)
g.tap('B'); g.run(120); sh(4)
g.tap('LEFT'); g.run(20); sh(5)   # can still move
g.close()
W=Image.new('RGB',(240*len(S),160))
for i,n in enumerate(S): W.paste(Image.open(f'/tmp/t2/lr{n}.png').convert('RGB'),(i*240,0))
W.save('/tmp/t2/lr_all.png')
