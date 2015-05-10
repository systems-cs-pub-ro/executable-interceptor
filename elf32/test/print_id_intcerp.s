# Do write(1, &function_id, 4) as a syscall.
# Arguments are passed in registers:
#    ebx <- 1
#    ecx <- &function_id
#    edx <- 4
# Syscall number (0x04) is passed in eax register.

interceptor:
	movl	$0x01, %ebx
	movl	%esp, %ecx
	movl	$0x04, %edx
	movl	$0x04, %eax
	int	$0x80
