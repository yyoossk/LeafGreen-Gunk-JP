#!/bin/bash
# regenerate JP comparison states from the current port ROM (EN states stay)
cd /home/claude/emu
{ echo "run 900"; echo "tap A 3"; echo "run 200"; echo "tap A 96"; echo "tap A 72"; echo "tap A 48"; echo "run 300"; echo "tap A 6"; echo "tap B 6"; echo "run 60"; echo "ss /tmp/jst_room.ss"; } | ./gbarun /home/claude/work/port.gba -
python3 /home/claude/tools/cmprun.py /tmp/scn_surf.txt /tmp/gst_room.ss /tmp/jst_room.ss | tail -1
