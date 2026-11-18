import sys,subprocess
import os
ROM=open(os.environ.get('DROM','/home/claude/roms/Pocket Monsters - LeafGreen (Japan) (Rev 1).gba'),'rb').read()
a=int(sys.argv[1],16)&0x1fffffe; n=int(sys.argv[2],16) if len(sys.argv)>2 else 0x100
a0=a-(0x08000000 if a>=0x08000000 else 0)
open('/tmp/f.bin','wb').write(ROM[a0:a0+n])
print(subprocess.run(['arm-none-eabi-objdump','-D','-bbinary','-marm','-Mforce-thumb','--adjust-vma=%#x'%(0x08000000+a0),'/tmp/f.bin'],capture_output=True,text=True).stdout.split('<.data>:')[1])
