#!/bin/bash
cd /home/claude/port; f=$1; o=$2
tools/preproc/preproc $f charmap.txt | cc -E -I include - | tools/preproc/preproc -ie $f charmap.txt | arm-none-eabi-as -mcpu=arm7tdmi --defsym LEAFGREEN=1 --defsym REVISION=1 --defsym ENGLISH=1 --defsym MODERN=0 -o $o
