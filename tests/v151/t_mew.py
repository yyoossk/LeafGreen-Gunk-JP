import sys; sys.path.insert(0,'/home/claude/tools')
from t151 import *
import cmprun
g=Game('jp','/tmp/walkst/s13_pewter_jp.ss',rom=ROM); g.run(30)
setflag(g,0x500+219)
print('tp',teleport(g,'POKEMON_MANSION_B1F',21,28))
sh=[]
def wait_act(n=200):
    for i in range(n):
        if g.in_battle() and g.u32(g.R['bcf'])==g.R['act']: return True
        g.tap('B'); 
    return False
# 1) diary -> battle -> run
r=talk(g,21,27,sh,'mew1',first='A',then='A',n=12); print('talk',r)
print('act',wait_act()); snap(g,'mew1_battle')
print('enemy species', g.u16(g.R['bmons']+0x58), 'lv', g.u8(g.R['bmons']+0x58+0x2A))
g.tap('D'); g.tap('R'); g.tap('A')
for i in range(60):
    if g.in_overworld() and g.idle(): break
    g.tap('B')
print('after run flag', getflag(g,0xF7), g.pos())
# 2) again -> catch with a Master Ball
sb=sb1(g); sb2=g.u32(0x03004FAC); key=g.u16(sb2+0xF20)
poke(g, sb+0x310, struct.pack('<HH',1,1^key))
r=talk(g,21,27,sh,'mew2',first='A',then='A',n=12); print('talk2',r)
print('act',wait_act())
g.tap('U'); g.tap('R'); g.tap('A'); g.run(60); snap(g,'mew2_bag0')
snap(g,'mew2_bagL')
g.tap('A'); g.run(20); snap(g,'mew2_sel'); g.tap('A'); g.run(20); snap(g,'mew2_use')
for i in range(80):
    if g.in_overworld() and g.idle(): break
    g.tap('B'); 
    if i<10: snap(g,f'mew2_after{i}')
print('caught flag', getflag(g,0xF7), 'count', count(g))
r=talk(g,21,27,sh,'mew3',first='A',then='A',n=12); print('talk3',r, g.in_battle())
