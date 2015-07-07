_start:
    .global _start
    .global dynamic_linker
    .global run_interceptor
    .global pre_main

dynamic_linker:
    pushl   %eax
    movl    $PLT0, %eax
    jmp     *%eax

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
    ret

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
