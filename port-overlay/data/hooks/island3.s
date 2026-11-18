	.section .island3,"ax"
	.syntax unified
	.thumb
	.align 2
	.global Island_QBInput
	.thumb_func
Island_QBInput:           @ HandleInputChooseAction: Quick Ball / Quick Run first
	push {lr}
	ldr r3, =JpQuickBall_Input
	bl 8f
	cmp r0, #0
	beq 1f
	pop {r3}
	ldr r3, =0x0802DD7D       @ handled: the function's epilogue
	bx r3
1:	ldr r0, =0x03003090
	ldrh r1, [r0, #46]
	pop {r3}
	bx r3
	.global Island_QBShow
	.thumb_func
Island_QBShow:            @ HandleChooseActionAfterDma3: the action menu is up, show the widget
	ldr r1, =0x0802DB81
	str r1, [r0]
	push {lr}
	ldr r3, =Gunk_QuickBall_Show
	bl 8f
	pop {r3}
	bx r3
8:	bx r3
	.pool

@ FRLG+ nature indicators: the SKILLS page's five stat prints go through these veneers (lr stays the caller's)
	.macro natveneer n
	.align 2
	.global Island_Nat\n
	.thumb_func
Island_Nat\n:
	bx pc
	nop
	.arm
	ldr ip, [pc]
	bx ip
	.word JpSum_PrintStat\n
	.thumb
	.endm
	natveneer 0
	natveneer 1
	natveneer 2
	natveneer 3
	natveneer 4
	.align 2
	.global Island_EggPidHigh
	.thumb_func
Island_EggPidHigh:
	bx pc
	nop
	.arm
	ldr ip, [pc]
	bx ip
	.word JpEggPidHigh
	.thumb
	.align 2
	.global Island_OpenContextMenu
	.thumb_func
Island_OpenContextMenu:
	bx pc
	nop
	.arm
	ldr ip, [pc]
	bx ip
	.word JpOpenContextMenuWrapper
	.thumb
	.align 2
	.global Island_TrainerParty
	.thumb_func
Island_TrainerParty:
	bx pc
	nop
	.arm
	ldr ip, [pc]
	bx ip
	.word JpCreateNPCTrainerPartyWrapper
	.thumb
	.align 2
	.global Island_MasterItemBlock
	.thumb_func
Island_MasterItemBlock:
	bx pc
	nop
	.arm
	ldr ip, [pc]
	bx ip
	.word JpMaster_ItemBlock
	.thumb
	.align 2
	.global Island_MasterEndDefeated
	.thumb_func
Island_MasterEndDefeated:
	bx pc
	nop
	.arm
	ldr ip, [pc]
	bx ip
	.word JpMaster_EndDefeated
	.thumb
