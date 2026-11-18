@ small stubs within BL range of the JP code (free 0xFF run at 0x08412484)
	.section .island,"ax"
	.syntax unified
	.thumb
	.align 2
	.global Island_ExpAllGate
	.thumb_func
Island_ExpAllGate:        @ Cmd_getexp state 2: r2 = (sentInPokes & 1) || GetsExpAllShare(expGetterMonId)
	push {r0, r1, r3, lr}
	movs r2, #1
	ands r2, r0
	bne 1f
	ldr r3, [r5]
	ldrb r0, [r3, #16]
	ldr r3, =GetsExpAllShare
	bl Island_CallR3
	adds r2, r0, #0
1:	pop {r0, r1, r3}
	pop {pc}

	.global Island_ExpAllDamage
	.thumb_func
Island_ExpAllDamage:      @ not sent in: Exp. Share -> 0 (share added later), else Exp. All -> exp/2 (at least 1)
	ldr r0, =gBattleMoveDamage
	movs r3, #0
	cmp r4, #25
	beq 2f
	mov r3, r9
	ldrh r3, [r3]
	lsrs r3, r3, #1
	bne 2f
	movs r3, #1
2:	str r3, [r0]
	bx lr

	.thumb_func
Island_CallR3:
	bx r3
	.pool

	.global Island_RegCheck
	.thumb_func
Island_RegCheck:          @ OpenContextMenu: Z set if itemId == registeredItem or == second registered item
	ldrh r3, [r1]
	cmp r0, r3
	beq 3f
	push {r0, r1, r2, r3, lr}
	ldr r0, =0x402A
	ldr r3, =VarGet
	bl Island_CallR3b
	ldr r1, [sp, #12]
	cmp r0, r1
	pop {r0, r1, r2, r3}
	pop {pc}
3:	bx lr
	.thumb_func
Island_CallR3b:
	bx r3
	.pool

	.global Island_HelpCheck
	.thumb_func
Island_HelpCheck:         @ RunHelpSystemCallback: in the field R belongs to the second registered item
	push {r2, r4, lr}
	ldrh r4, [r2, #46]
	movs r0, #128
	lsls r0, r0, #1
	tst r4, r0
	beq 9f
	ldr r0, [r2]
	ldr r1, =0x08055DD1
	cmp r0, r1
	bne 9f
	ldr r0, =0x402A
	ldr r3, =VarGet
	bl Island_CallR3b
	cmp r0, #0
	beq 9f
	movs r0, #128
	lsls r0, r0, #1
	bics r4, r0
9:	ldr r3, =Gunk_IsChoosingBattleAction
	bl Island_CallR3b
	cmp r0, #0
	beq 10f
	movs r0, #192
	lsls r0, r0, #2
	bics r4, r0
10:	adds r1, r4, #0
	movs r0, #192
	pop {r2, r4}
	pop {r3}
	bx r3
	.pool

	.global Island_RMark
	.thumb_func
Island_RMark:             @ BagListMenuItemPrintFunc: r0 = registeredItem, r7 = itemId, r8 = window, r6 = y
	cmp r0, r7
	bne 1f
	bx lr                     @ the SELECT one: back to the vanilla blit
1:	push {r4, lr}
	ldr r0, =0x402A
	ldr r3, =VarGet
	bl Island_CallR3c
	cmp r0, r7
	bne 2f
	sub sp, #20
	str r6, [sp, #0]
	movs r0, #0
	str r0, [sp, #4]
	str r0, [sp, #8]
	movs r0, #255
	str r0, [sp, #12]
	movs r0, #1
	str r0, [sp, #16]
	mov r0, r8
	movs r1, #0
	ldr r2, =gJpText_RButton
	movs r3, #116
	ldr r4, =0x0810C3C9
	bl Island_CallR4
	add sp, #20
2:	pop {r4}
	pop {r3}
	ldr r3, =0x0810922B      @ skip to the function's end
	bx r3
	.thumb_func
Island_CallR3c:
	bx r3
	.thumb_func
Island_CallR4:
	bx r4
	.pool
