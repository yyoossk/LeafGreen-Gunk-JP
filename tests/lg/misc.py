import sys,struct; sys.path.insert(0,'/home/claude/tools')
from walker import *
g=Game('jp','/tmp/walkst/s21_postgame_jp.ss',rom=sys.argv[1]); g.run(10)
def runscript(data):
    buf=g.R['strbuf']+0x200
    for i,b in enumerate(data): g.cmd(f'poke {buf+i:08X} {b:02X}')
    for a,v in ((0x03000EB1,b'\x01'),(0x03000EB0,b'\x00'),(0x03000EB8,struct.pack('<I',buf)),(0x03000EA8,b'\x00')):
        for i,b in enumerate(v): g.cmd(f'poke {a+i:08X} {b:02X}')
print('silph mb flag',g.getflag(0x250))
# legends
for f in (0x82,0x2BE,0x5D,0x2BF,0x52,0x2BD,0x81,0x2BC): g.setflag(f)
runscript(bytes([4])+struct.pack('<I',0x0870e568)+b'\x02'); g.run(60)
print('after HoF flags', [g.getflag(f) for f in (0x82,0x2BE,0x5D,0x2BF,0x52,0x2BD,0x81,0x2BC)])
# daycare text
runscript(bytes([4])+struct.pack('<I',0x0870e530)+b'\x02'); g.run(40)
for i in range(4): g.shot(f'/tmp/t2/dc{i}.png'); g.tap('A'); g.run(30)
g.run(60)
g.teleport('INDIGO_PLATEAU_POKEMON_CENTER_1F',2,7); g.face('L'); g.run(20)
g.tap('A'); g.run(60); g.tap('A'); g.run(60); g.shot('/tmp/t2/mart0.png'); g.tap('A'); g.run(60); g.shot('/tmp/t2/mart1.png')
g.close()
