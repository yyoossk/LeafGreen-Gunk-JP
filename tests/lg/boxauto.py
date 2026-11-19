import sys, struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp','/tmp/walkst/s21_postgame_jp.ss',rom='/home/claude/work/port.gba'); g.run(10)
g.cmd(f'poke {g.R["cnt"]:08X} 06')
print('box var before', g.getvar(0x4037))
buf=g.R['strbuf']+0x200
one=bytes([0x79])+struct.pack('<HBH',16,5,0)+bytes(9)
for rnd in range(3):
    data=one*20+b'\x02'
    for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
        for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
    g.run(60); print('ptr', hex(g.u32(0x03000EB8)-buf), g.u8(0x03000EA8))
    print('after', (rnd+1)*20, 'box var', g.getvar(0x4037), 'fullmsg flag', g.getflag(0x843), 'result', g.u16(0x020370D0) if False else '')
g.close()
