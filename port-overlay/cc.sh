#!/bin/bash
# usage: cc.sh src.c out.o
set -o pipefail
cc -E -iquote include -Wno-trigraphs -DLEAFGREEN -DREVISION=1 -DENGLISH -DMODERN=0 -I tools/agbcc/include -I tools/agbcc -nostdinc -undef -std=gnu89 "$1" | tools/preproc/preproc -i "$1" charmap.txt | tools/agbcc/bin/agbcc -mthumb-interwork -Wimplicit -Wparentheses -Werror -O2 -fhex-asm -o - - | cat - <(echo -e ".text\n\t.align\t2, 0") | arm-none-eabi-as -mcpu=arm7tdmi --defsym LEAFGREEN=1 --defsym REVISION=1 --defsym ENGLISH=1 --defsym MODERN=0 -o "$2" -
