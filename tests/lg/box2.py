import sys, struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp','/tmp/walkst/s21_postgame_jp.ss',rom=sys.argv[1]); g.run(10)
g.cmd(f'poke {g.R["cnt"]:08X} 06')
SP=0x0203AE88  # placeholder
buf=g.R['strbuf']+0x200
one=bytes([0x79])+struct.pack('<HBH',16,5,0)+bytes(9)
def give(n):
    data=one*n+b'\x02'
    for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
        for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
k=0
ps=g.u32(0x03004FB0); print('currentBox',g.u8(ps),'var',g.getvar(0x4037))
for rnd in range(3):
    give(20); g.run(40)
    for j in range(6):
        g.run(30)
        g.shot(f'/tmp/t2/bx{k:02d}.png'); k+=1
        g.tap('A')
print('idle',g.idle(),'ctx',g.u8(0x03000EA8),g.u8(0x03000EB1)); g.hold('R',20); g.run(60)
print('dbg',g.u16(0x02022088),g.u16(0x0202208A),hex(g.u16(0x0202208C))); print('currentBox after',g.u8(ps),'var',g.getvar(0x4037))
for i in range(6):
    g.run(120); g.shot(f'/tmp/t2/by{i}.png'); print('ctx',hex(g.u32(0x03000EB8)),g.u8(0x03000EA8),g.u8(0x03000EB1),'cb2',hex(g.cb2()),'cb1',hex(g.u32(g.R['main']))); g.tap('A')
print('end idle',g.idle(),'frame pc'); g.cmd('regs'); print(g.p.stdout.readline())
g.close()
