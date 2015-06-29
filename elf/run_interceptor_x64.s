run_interceptor:
    popq    %rax
    popq    %r10
    cmpq    $0, %r10
    jne     direct
    pushq    %rax
    movq    $PLT0, %r10
direct:
    jmp     *%r10

pre_main:
    movq    $ENTRY, %rax
    jmpq    *%rax
