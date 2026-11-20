import sys; sys.path.insert(0,'/home/claude/tools')
from walker import *
import walker
from PIL import Image
rom=sys.argv[1]; tag=sys.argv[2]; st=sys.argv[3]
maps=[m for m in walker._MAPS if 'SSANNE' in m and 'ROOM' in m]
g=Game('jp',st,rom=rom); g.run(10)
for i,m in enumerate(maps):
    g.teleport(m,3,4); g.run(90); g.shot(f'/tmp/t7/sr_{tag}{i}.png')
g.close(); print(maps)
