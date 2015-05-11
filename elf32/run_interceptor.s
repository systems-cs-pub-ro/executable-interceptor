dynamic_linker:
	push	%eax
	movl	$PLT0, %eax
	jmp	*%eax

run_interceptor:
	movl	(%esp), %eax
	movl	REL_PLT + 4(%eax), %eax # .rel.plt
	shr	$8, %eax
	shl	$4, %eax
	movl	DYN_SYM(%eax), %eax # .dynsym
	leal	DYN_STR(%eax), %eax # .dynstr
	push	%eax
	call	interceptor
	pop	%eax
	pop	%eax
	ret
