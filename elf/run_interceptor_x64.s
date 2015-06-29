_start:
    .global _start
    .global run_interceptor
    .global pre_main

run_interceptor:
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
