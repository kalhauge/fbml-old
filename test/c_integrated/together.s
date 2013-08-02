	.section	__TEXT,__text,regular,pure_instructions
	.globl	_multi_add
	.align	4, 0x90
_multi_add:                             ## @multi_add
	.cfi_startproc
## BB#0:                                ## %entry
	addl	%ecx, %edx
	addl	%esi, %edi
	addl	%edx, %edi
	movl	%edi, (%r8)
	ret
	.cfi_endproc

	.globl	_multiply_with_four
	.align	4, 0x90
_multiply_with_four:                    ## @multiply_with_four
	.cfi_startproc
## BB#0:                                ## %entry
	pushq	%rax
Ltmp1:
	.cfi_def_cfa_offset 16
	movq	%rsi, %rax
	movl	%edi, %esi
	movl	%edi, %edx
	movl	%edi, %ecx
	movq	%rax, %r8
	callq	_multi_add
	popq	%rax
	ret
	.cfi_endproc

	.globl	_main
	.align	4, 0x90
_main:                                  ## @main
	.cfi_startproc
## BB#0:
	pushq	%rbp
Ltmp7:
	.cfi_def_cfa_offset 16
	pushq	%r15
Ltmp8:
	.cfi_def_cfa_offset 24
	pushq	%r14
Ltmp9:
	.cfi_def_cfa_offset 32
	pushq	%rbx
Ltmp10:
	.cfi_def_cfa_offset 40
	pushq	%rax
Ltmp11:
	.cfi_def_cfa_offset 48
Ltmp12:
	.cfi_offset %rbx, -40
Ltmp13:
	.cfi_offset %r14, -32
Ltmp14:
	.cfi_offset %r15, -24
Ltmp15:
	.cfi_offset %rbp, -16
	movq	%rsi, %rbp
	movq	8(%rbp), %rdi
	callq	_atoi
	movl	%eax, %r14d
	movq	16(%rbp), %rdi
	callq	_atoi
	movl	%eax, %r15d
	movq	24(%rbp), %rdi
	callq	_atoi
	movl	%eax, %ebx
	movq	32(%rbp), %rdi
	callq	_atoi
	movl	%eax, %ebp
	leaq	4(%rsp), %r8
	movl	%r14d, %edi
	movl	%r15d, %esi
	movl	%ebx, %edx
	movl	%ebp, %ecx
	callq	_multi_add
	leaq	L_.str(%rip), %rdi
	movl	%r14d, %esi
	movl	%r15d, %edx
	movl	%ebx, %ecx
	movl	%ebp, %r8d
	xorb	%al, %al
	callq	_printf
	leaq	L_.str1(%rip), %rdi
	movl	4(%rsp), %esi
	xorb	%al, %al
	callq	_printf
	xorl	%eax, %eax
	addq	$8, %rsp
	popq	%rbx
	popq	%r14
	popq	%r15
	popq	%rbp
	ret
	.cfi_endproc

	.section	__TEXT,__cstring,cstring_literals
L_.str:                                 ## @.str
	.asciz	 "Ran function with args: %d %d %d %d \n"

L_.str1:                                ## @.str1
	.asciz	 "The result was: %d \n"


.subsections_via_symbols
