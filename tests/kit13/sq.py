import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
from PIL import Image
g=Game('jp','/tmp/t13/s.ss',rom=sys.argv[1]); g.run(10)
S=[]
def sh():
    n=len(S); g.shot(f'/tmp/t13/sq{n}.png'); S.append(n)
g.teleport('VERMILION_CITY',int(sys.argv[2]),int(sys.argv[3])); g.run(120); g.shot('/tmp/t13/pos.png'); g.tap('U'); g.run(20)
def talk(): g.tap('A'); g.run(70)
# 1 no badge
talk(); sh(); g.tap('A'); g.run(60); sh(); g.tap('A'); g.run(60)
for i in range(4): g.tap('B'); g.run(30)
g.setflag(0x822)
# 2 badge, decline
talk(); sh(); g.tap('A'); g.run(60); sh(); g.tap('A'); g.run(60); sh(); g.tap('B'); g.run(60); sh(); g.tap('A'); g.run(60)
for i in range(4): g.tap('B'); g.run(30)
# 3 accept
talk(); g.tap('A'); g.run(60); g.tap('A'); g.run(60); g.tap('A'); g.run(250); sh()
for i in range(10): g.tap('B'); g.run(40)
# 4 after
talk(); sh()
g.close()
W=Image.new('RGB',(240*4,160*((len(S)+3)//4)))
for i in S: W.paste(Image.open(f'/tmp/t13/sq{i}.png').convert('RGB'),((i%4)*240,(i//4)*160))
W.save('/tmp/t13/sq.png')
