import sys; sys.path.insert(0,'/home/claude/tools')
import cmprun,os
scn=open(sys.argv[1]).read(); tag=os.path.basename(sys.argv[1]).split('.')[0].replace('_','-')
logs=cmprun.build(scn,'jp',{'jp':sys.argv[2],'en':''},tag)
for l in logs: print(l)
from PIL import Image
shots=sorted(f for f in os.listdir('/tmp') if f.startswith(f'cmp_{tag}_') and f.endswith('_jp.png'))
n=len(shots); cols=4; rows=(n+cols-1)//cols
W=Image.new('RGB',(240*cols,160*rows))
for i,f in enumerate(shots): W.paste(Image.open('/tmp/'+f),(240*(i%cols),160*(i//cols)))
W.save(f'/tmp/jp_{tag}.png'); print('shots',n)
