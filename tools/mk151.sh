#!/bin/bash
# build the 151匹揃う版 (everything in mk.sh + port/v151) -> /home/claude/work/port151.gba
set -e
cd /home/claude/port
./cc.sh src/gunk_follower.c pb/gunk_follower.o
./cc.sh src/hooks/hk_event_object_movement.c pb/hk_eom.o
for f in src/hooks/*.c; do b=$(basename $f .c); [ $b = hk_event_object_movement ] && continue; ./cc.sh $f pb/$b.o; done
for f in data/hooks/*.s; do b=$(basename $f .s); /home/claude/tools/asm.sh $f pb/$b.o; done
rm -f pb151/*.o
for f in v151/*.c; do [ -e "$f" ] || continue; b=$(basename $f .c); ./cc.sh $f pb151/$b.o; done
for f in v151/*.s; do [ -e "$f" ] || continue; b=$(basename $f .s); /home/claude/tools/asm.sh $f pb151/$b.o; done
python3 /home/claude/tools/gxbuild.py > /tmp/gx.log 2>&1 || { grep -v kept /tmp/gx.log; exit 1; }
V151=1 python3 /home/claude/tools/build_port.py | grep -iE "error|missing|undefined" || true
V151=1 python3 /home/claude/tools/patch_port.py /home/claude/roms/"Pocket Monsters - LeafGreen (Japan) (Rev 1).gba" /home/claude/work/port151.gba | grep -iE "error|Trace|assert|v151" || true
echo BUILD151_OK
