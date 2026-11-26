#!/bin/bash
# rebuild everything: hooks C, follower, data .s, link, patch
set -e
cd /home/claude/port
./cc.sh src/gunk_follower.c pb/gunk_follower.o
./cc.sh src/hooks/hk_event_object_movement.c pb/hk_eom.o
for f in src/hooks/*.c; do b=$(basename $f .c); [ $b = hk_event_object_movement ] && continue; ./cc.sh $f pb/$b.o; done
for f in data/hooks/*.s; do b=$(basename $f .s); /home/claude/tools/asm.sh $f pb/$b.o; done
python3 /home/claude/tools/gxbuild.py > /tmp/gx.log 2>&1 || { grep -v kept /tmp/gx.log; exit 1; }
python3 /home/claude/tools/build_port.py | grep -iE "error|missing|undefined" || true
python3 /home/claude/tools/patch_port.py > /tmp/pp.log 2>&1 || { grep -iE "error|Trace|assert|line" /tmp/pp.log | tail -5; echo BUILD_FAILED; exit 1; }
grep -iE "error|assert" /tmp/pp.log || true
[ -n "$MKSTATES" ] && /home/claude/tools/mkstates.sh >/dev/null
echo BUILD_OK
