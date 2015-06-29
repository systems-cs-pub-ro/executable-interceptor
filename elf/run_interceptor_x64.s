_start:
    .global _start
    .global run_interceptor
    .global pre_main

run_interceptor:
    movq    (%rsp), %rax
    shl     $3, %rax
    movq    REL_PLT + 8(%rax,%rax,2), %rax
    shr     $32, %rax
    shl     $3, %rax
    movl    DYN_SYM(%rax,%rax,2), %eax
    leaq    DYN_STR(%eax), %rax
    popq    %rax
    popq    %r10
    cmpq    $0, %r10
    jne     direct
    pushq    %rax
    .equ    e, _start - . + PLT0
    jmp     . + e
direct:
    jmp     *%r10

pre_main:
    .equ    d, _start - . + ENTRY
    jmp     . + d
