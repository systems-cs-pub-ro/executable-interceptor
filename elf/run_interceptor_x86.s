    .text

_start:
    .global _start
    .global dynamic_linker
    .equ    red_zone_words, 0x10

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
    movl    $red_zone_words, %ecx
    subl    $((red_zone_words - 1)*4), %esp
downstack:
    movl    ((red_zone_words - 1)*4)(%esp), %edx
    movl    %edx, (%esp)
    addl    $4, %esp
    loop    downstack
    subl    $(red_zone_words*4), %esp
    .equ    ra, run_ret_interceptor - _start + VA
    movl    $ra, 4(%esp)
    ret

run_ret_interceptor:
    add     $((red_zone_words - 2)*4), %esp
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
