import sys, struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom=sys.argv[1]
g=Game('jp','/tmp/t2/after_reload.ss',rom=rom); g.run(10)
def runscript(data):
    buf=g.R['strbuf']+0x200
    for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
        for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
    g.run(30)
BS=0x0885e069
# Brock scene without shoes
runscript(bytes([4])+struct.pack('<I',BS)+b'\x02')
print('no shoes: var',g.getvar(0x406C),'hide aide',g.getflag(0x92),'hide guide',g.getflag(0x2E))
g.setflag(0x82F); g.setflag(0x92); g.setvar(0x406C,0)
runscript(bytes([4])+struct.pack('<I',BS)+b'\x02')
print('shoes: var',g.getvar(0x406C),'hide aide',g.getflag(0x92))
g.setvar(0x406C,0)
# menu PC
g.tap('START'); g.run(20); g.tap('DOWN',2); g.run(10); g.shot('/tmp/t2/p0.png')
g.tap('A'); g.run(80); g.shot('/tmp/t2/p1.png')
g.tap('A'); g.run(60); g.shot('/tmp/t2/p2.png')
g.tap('A'); g.run(60); g.shot('/tmp/t2/p3.png')   # storage
g.tap('A'); g.run(200); g.shot('/tmp/t2/p4.png')
g.tap('B',3); g.run(200); g.shot('/tmp/t2/p5.png')
g.tap('B',2); g.run(100); g.shot('/tmp/t2/p6.png')
g.tap('B',2); g.run(100); g.shot('/tmp/t2/p7.png')
g.tap('B',2); g.run(100); g.shot('/tmp/t2/p8.png')
print('idle',g.idle(), g.pos())
# real PC in Viridian center? use player's 2F PC
g.teleport('PALLET_TOWN_PLAYERS_HOUSE_2F',1,2); g.face('U'); g.run(10)
g.tap('A'); g.run(80); g.shot('/tmp/t2/q0.png')
g.tap('A'); g.run(60); g.tap('B'); g.run(60); g.shot('/tmp/t2/q1.png')
g.tap('B',2); g.run(100); g.shot('/tmp/t2/q2.png'); print('idle2',g.idle())
g.close()
