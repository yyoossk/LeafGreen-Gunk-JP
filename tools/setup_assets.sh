#!/bin/bash
# 生成物（ROM・ほかのリポジトリから作るファイル）を /home/claude/port に用意する
set -e
P=/home/claude/port
cp -r /home/claude/gunk/graphics/gunk_followers $P/graphics/
cp /home/claude/gunk/graphics/misc/emoticons.4bpp $P/graphics/misc/emoticons_gunk.4bpp
F=/home/claude/frlgplus/data/tilesets/secondary/pokemon_center
cp $F/tiles.4bpp.lz $P/data/hooks/room2ts/
for i in $(seq 0 15); do cp $F/palettes/$(printf %02d $i).gbapal $P/data/hooks/room2ts/; done
python3 /home/claude/tools/gen_master.py
