run_interceptor:
    push    {r0, r1}
    ldr     r0, [ip]
    and     r1, r0, #0x0ff00000
    add     ip, ip, r1
    and     r1, r0, #0x000ff000
    add     ip, ip, r1
    and     r1, r0, #0x00000ff0
    add     ip, ip, r1
    and     r1, r0, #0x0000000f
    add     ip, ip, r1
    ldr     r0, [ip]
    push    {r0}
    add     sp, sp, #4
    pop     {r0, r1}
    ldr     pc, [sp, #-12]
