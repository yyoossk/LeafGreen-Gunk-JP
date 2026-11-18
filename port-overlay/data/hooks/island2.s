	.section .island2,"ax"
	.syntax unified
	.thumb
	.align 2
	.global Island_SumIvEv
	.thumb_func
Island_SumIvEv:           @ JP BufferMonSkills after the speed row: apply the IV/EV view, redo r6/r0
	push {lr}
	ldr r3, =JpSum_IvEv
	bl 8f
	ldr r6, =0x0203B0B4
	ldr r0, [r6]
	pop {r3}
	bx r3
	.global Island_SumA
	.thumb_func
Island_SumA:              @ A pressed, r0 = curPageIndex (not INFO): MOVES -> vanilla path, SKILLS -> cycle
	cmp r0, #2
	bne 1f
	ldr r3, =0x081351B3
	bx r3
1:	cmp r0, #1
	bne 2f
	push {lr}
	ldr r3, =JpSum_CycleView
	bl 8f
	pop {r3}
	bx r3
2:	bx lr
	.global Island_SumOpen
	.thumb_func
Island_SumOpen:           @ summary screen load: start on the stats view
	ldr r0, =gJpGunkStatView
	movs r1, #0
	strb r1, [r0]
	ldr r3, =0x08136A9D
	bx r3
8:	bx r3
	.pool
