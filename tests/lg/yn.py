import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp','/tmp/walkst/s21_postgame_jp.ss',rom=sys.argv[1]); g.run(10)
addr=int(sys.argv[2],16)|1
buf=g.R['strbuf']+0x200
data=bytes([0x23])+struct.pack('<I',addr)+bytes([0x27,0x02])  # callnative; waitstate? just end
data=bytes([0x23])+struct.pack('<I',addr)+bytes([0x02])
for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
    for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
g.run(30); g.shot('/tmp/t2/yn.png'); g.close()
