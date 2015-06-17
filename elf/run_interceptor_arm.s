run_interceptor:
    push    {r0}
    sub     r0, pc, #12
    sub     r0, r0, #ASLR4, 8
    sub     r0, r0, #ASLR3, 16
    sub     r0, r0, #ASLR2, 24
    sub     r0, r0, #ASLR1  @ r0 has the ASLR offset
    pop     {r0}
    add     ip, ip, #C3, 12
    add     ip, ip, #C2, 20
    add     ip, ip, #C1, 28
    add     ip, ip, #C0
    ldr     pc, [ip]
