_start:
    .global _start
    .global run_interceptor
    .global pre_main

run_interceptor:
    movl    (%esp), %eax
    movl    REL_PLT + 4(%eax), %eax
    shr     $8, %eax
    shl     $4, %eax
    movl    DYN_SYM(%eax), %eax
    leal    DYN_STR(%eax), %eax
    pushl   %eax
    pushl   $ADDITIONAL_DATA
    call    interceptor
    addl    $8, %esp
    popl    %eax
    popl    %edx
    test    %edx, %edx
    jnz     direct
    pushl   %eax
    movl    $PLT0, %eax
    jmp     *%eax
direct:
    jmp     *%edx

pre_main:
    # need to save the initial state because if some register is changed,
    # something nasty will happen when the exit function is called
    pusha
    pushl   $ADDITIONAL_DATA
    call    init
    addl    $4, %esp
    popa
    movl    $ENTRY, %eax
    jmp     *%eax
