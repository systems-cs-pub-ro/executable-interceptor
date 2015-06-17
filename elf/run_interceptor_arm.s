run_interceptor:
    push    {r0}
    ldr     r0, =-(ASLR + 16)
    add     r0, r0, pc  @ r0 = ASLR offset for this process
    ldr     r0, =C
    add     ip, ip, r0
    pop     {r0}
    ldr     pc, [ip]
