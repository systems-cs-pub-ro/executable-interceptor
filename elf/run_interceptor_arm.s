run_interceptor:
    push    {r0, r1}
    ldr     r0, = . + VA + 12
    sub     r0, pc, r0  @ r0 = ASLR offset for this process
    ldr     r1, =C
    add     r1, r1, r0
    add     ip, r1, ip, LSL #2
    pop     {r0, r1}
    ldr     pc, [ip]
