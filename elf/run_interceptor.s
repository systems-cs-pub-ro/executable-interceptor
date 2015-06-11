dynamic_linker:
    pushl  %eax
    movl   $PLT0, %eax
    jmp    *%eax

run_interceptor:
    movl   (%esp), %eax
    movl   REL_PLT + 4(%eax), %eax
    shr    $8, %eax
    shl    $4, %eax
    movl   DYN_SYM(%eax), %eax
    leal   DYN_STR(%eax), %eax
    pushl  %eax
    pushl  $ADDITIONAL_DATA
    call   interceptor
    popl   %eax
    popl   %eax
    popl   %eax
    ret

pre_main:
    # mmap(0, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0)
    pusha
    movl    $0xc0, %eax
    xorl    %ebx, %ebx
    movl    $4096, %ecx
    movl    $3, %edx
    movl    $34, %esi
    movl    $-1, %edi
    xorl    %ebp, %ebp
    int     $0x80
    movl    %eax, ADDITIONAL_DATA
    popa
    movl    $ENTRY, %eax
    jmp     *%eax
