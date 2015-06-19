    .text

_start:
    .global _start
    .global pre_main
    .global run_interceptor
    .global run_ret_interceptor

run_interceptor:
    @ prepare stack for returning
    sub     sp, sp, #4      @ space for lr
    push    {ip}
    sub     sp, sp, #8      @ space for ASLR and fname
    push    {r0-r11, lr}
    bl      compute_aslr
    bl      compute_fname

    push    {r0, r1, ip}
    mov     r0, ip
    @ call interceptor
    pop     {r0, r1, ip}

    @ call the original function
    bl      compute_ip

    str     r0, [sp, #13*4] @ save ASLR
    str     r1, [sp, #14*4] @ save fname

    pop     {r0-r11, lr}

    @ save the original return address
    str     lr, [sp, #12]   @ save lr

    @ return set to run_ret_interceptor
    push    {r0}
    ldr     r0, [sp, #4]    @ aslr
    .set    dist_ret, run_ret_interceptor + VA - _start
    ldr     lr, =dist_ret
    add     lr, lr, r0
    pop     {r0}
    ldr     pc, [ip]

run_ret_interceptor:
    @ r1 will be ASLR and r2 fname
    pop     {r1, r2, ip, lr}
    @ call ret_interceptor
    mov     pc, lr

compute_aslr:
    .set    PC, . + VA + 12 - _start
    ldr     r0, =PC
    sub     r0, pc, r0  @ r0 = ASLR offset for this process
    mov     pc, lr

compute_fname:
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
    mov     pc, lr

compute_ip:
    ldr     r2, =C
    add     r2, r2, r0
    add     ip, r2, ip, LSL #2
    mov     pc, lr
