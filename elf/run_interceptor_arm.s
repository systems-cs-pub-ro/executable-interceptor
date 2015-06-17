run_interceptor:
    add     ip, ip, #C3, 12
    add     ip, ip, #C2, 20
    add     ip, ip, #C1, 28
    add     ip, ip, #C0
    ldr     pc, [ip]
