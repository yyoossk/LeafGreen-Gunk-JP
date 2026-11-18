import sys; sys.path.insert(0,'/home/claude/tools')
from t151 import *
g=Game('jp','/tmp/walkst/s13_pewter_jp.ss',rom=ROM); g.run(30)
sh=[]
# dojo
print('tp',teleport(g,'SAFFRON_CITY_DOJO',6,4)); setcount(g,1)
print('lee',talk(g,5,3,sh,'dojo_lee'),count(g),getflag(g,0x278))
print('chan',talk(g,7,3,sh,'dojo_chan'),count(g))
# fossils
setflag(g,0x500+170)
print('tp',teleport(g,'MT_MOON_B2F',13,9)); 
bag0=g.peek(sb1(g)+0x3B8,40).hex()
print('dome',talk(g,13,7,sh,'fossil',first='A',then='A'))
print('keyitems',g.peek(sb1(g)+0x3B8,40).hex(), 'flags',getflag(g,0x272),getflag(g,0x273),getflag(g,0x232))
print('helix again',talk(g,14,7,sh,'fossil2',first='A',then='A'))
# NPC gifts
setcount(g,1)
print('tp',teleport(g,'CERULEAN_CITY_HOUSE3',8,4))
print('bulba',talk(g,9,3,sh,'bulba'),count(g),getflag(g,0xF0))
print('bulba2',talk(g,9,3,sh,'bulba2'),count(g))
print('tp',teleport(g,'ROUTE24',6,9))
print('char',talk(g,6,8,sh,'char'),count(g),getflag(g,0xF1))
print('tp',teleport(g,'VERMILION_CITY',17,9))
setflag(g,0x822,False)
print('squirt nobadge',talk(g,17,8,sh,'sq0'),count(g),getflag(g,0xF2))
setflag(g,0x822,True)
print('squirt',talk(g,17,8,sh,'sq1'),count(g),getflag(g,0xF2))
g.save('/tmp/t151/gifts.ss'); g.close()
