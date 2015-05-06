run_interceptor:
	movl	(%esp), %eax
	movl	0x080482b4(%eax), %eax # .rel.plt
	shr	$8, %eax
	shl	$4, %eax
	movl	0x080481cc(%eax), %eax # .dynsym
	leal	0x0804822c(%eax), %eax # .dynstr
	push	%eax
	call	interceptor
	pop	%eax
	pop	%eax
	ret
