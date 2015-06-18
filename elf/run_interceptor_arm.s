run_interceptor:
    push    {r0, r1, r2}
    ldr     r0, = . + VA + 12 - run_interceptor
    sub     r0, pc, r0  @ r0 = ASLR offset for this process
    ldr     r1, =REL_PLT
    add     r2, r1, r0
    add     r2, r2, ip, LSL #3
    ldr     r2, [r2, #4]
    lsr     r2, #8
    ldr     r1, =DYNSYM
    add     r1, r1, r0
    ldr     r2, [r1, r2, LSL #4]
    ldr     r1, =DYNSTR
    add     r1, r1, r0
    add     r1, r2, r1  @ r1 = function name
    push    {r0-r12}
    mov     r2, r1
    @ write(1, function_name, 10)
    mov     r0, #0
    mov     r2, r1
while:
    ldrb    r3, [r2]
    add     r0, r0, #1
    add     r2, r2, #1
    cmp     r3, #0
    bne     while
    sub     r2, r0, #1
    mov     r0, #1
    mov     r7, #4
    swi     #0
    @ write(1, "\n", 1)
    mov     r0, #1
    ldr     r1, =nl
    add     r1, r1, pc
    ldr     r4, = . + 4
    sub     r1, r1, r4
    mov     r2, #1
    mov     r7, #4
    swi     #0
    pop     {r0-r12}
    @ call the original function
    ldr     r1, =C
    add     r1, r1, r0
    add     ip, r1, ip, LSL #2
    pop     {r0, r1, r2}
    @ save the original return address
    push    {lr}
    @ return to run_ret_interceptor
    .set    distance, run_ret_interceptor + VA - run_interceptor
    ldr     lr, =distance
    ldr     pc, [ip]

run_ret_interceptor:
    @ return to the original place
    pop     {pc}

nl:
    .asciz "\n"
