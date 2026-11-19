import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp','/tmp/walkst/s21_postgame_jp.ss',rom=sys.argv[1]); g.run(10)
buf=g.R['strbuf']+0x200
# setwildbattle SPECIES_STARYU(120) lv 30 item 0 ; dowildbattle
data=bytes([0xB6])+struct.pack('<HBH',120,30,0)+bytes([0xB7,0x02])
for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
    for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
for i in range(30):
    g.run(30)
    if g.in_battle(): break
g.run(400); g.tap('A'); g.run(200); g.shot(sys.argv[2]+'0.png')
g.tap('A'); g.run(40); g.shot(sys.argv[2]+'1.png')
g.tap('S'); g.run(20); g.shot(sys.argv[2]+'2.png')
g.tap('S'); g.run(20); g.shot(sys.argv[2]+'3.png')
g.tap('S'); g.run(20); g.run(1); g.shot(sys.argv[2]+'4.png')
g.tap('D'); g.run(20); g.shot(sys.argv[2]+'5.png')
g.close()
