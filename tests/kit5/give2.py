import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
rom=sys.argv[1]; tag=sys.argv[2]
g=Game('jp','/tmp/t4/fresh_new.ss',rom=rom); g.run(30)
def runscript(data):
    buf=g.R['strbuf']+0x200
    for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
        for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
for k,item in enumerate((13,200)):
    runscript(bytes([0x6A,0x1A,0x00,0x80])+struct.pack('<H',item)+bytes([0x1A,0x01,0x80,0x01,0x00,0x09,0x01,0x6B,0x02]))
    g.run(120); g.shot(f'/tmp/t5/{tag}_gv{k}.png')
    for i in range(12): g.tap('A'); g.run(20)
sb=g.sb1()
print(tag,'med',[g.u16(sb+0x348C+4*i) for i in range(3)],'held',[g.u16(sb+0x352C+4*i) for i in range(3)], g.script_running())
g.close()
