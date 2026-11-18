@ FRLG+'s Pokémon Center tileset (it adds the basement's mat, paintings and healing machine metatiles),
@ used only by the Seven Island house basement
	.section .rodata
	.align 2
	.global gJpTileset_BattleHouse
gJpTileset_BattleHouse:
	.byte 1, 1, 0, 0
	.4byte gJpBHTiles, gJpBHPalettes, gJpBHMetatiles, 0, gJpBHMetatileAttributes
	.align 2
gJpBHTiles:
	.incbin "data/hooks/room2ts/tiles.4bpp.lz"
	.align 2
gJpBHPalettes:
	.incbin "data/hooks/room2ts/00.gbapal"
	.incbin "data/hooks/room2ts/01.gbapal"
	.incbin "data/hooks/room2ts/02.gbapal"
	.incbin "data/hooks/room2ts/03.gbapal"
	.incbin "data/hooks/room2ts/04.gbapal"
	.incbin "data/hooks/room2ts/05.gbapal"
	.incbin "data/hooks/room2ts/06.gbapal"
	.incbin "data/hooks/room2ts/07.gbapal"
	.incbin "data/hooks/room2ts/08.gbapal"
	.incbin "data/hooks/room2ts/09.gbapal"
	.incbin "data/hooks/room2ts/10.gbapal"
	.incbin "data/hooks/room2ts/11.gbapal"
	.incbin "data/hooks/room2ts/12.gbapal"
	.incbin "data/hooks/room2ts/13.gbapal"
	.incbin "data/hooks/room2ts/14.gbapal"
	.incbin "data/hooks/room2ts/15.gbapal"
	.align 2
gJpBHMetatiles:
	.incbin "data/hooks/room2ts/metatiles.bin"
	.align 2
gJpBHMetatileAttributes:
	.incbin "data/hooks/room2ts/metatile_attributes.bin"
