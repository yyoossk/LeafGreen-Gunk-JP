import sys,glob
from PIL import Image
out=sys.argv[1]; fs=[]
for p in sys.argv[2:]: fs+=sorted(glob.glob(p))
cols=4; rows=(len(fs)+cols-1)//cols
W=Image.new('RGB',(240*cols,160*rows))
for i,f in enumerate(fs): W.paste(Image.open(f).convert('RGB'),(240*(i%cols),160*(i//cols)))
W.save(out); print(len(fs))
