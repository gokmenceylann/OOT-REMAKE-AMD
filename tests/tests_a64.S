.text
.global fixture
fixture:
    stp x30, xzr, [sp, #-16]!
    subs w0, w0, #1
    b.eq zero
    adr x8, nested
    blr x8
    ldp x30, xzr, [sp], #16
    ret
zero:
    ldp x30, xzr, [sp], #16
    mov w0, #42
    ret
nested:
    fadd d0, d1, d2
    eor v3.16b, v1.16b, v2.16b
    mov w9, #0x1234
    movk w9, #0xabcd, lsl #16
    lsl w10, w9, #1
    lsr w11, w10, #3
    asr w12, w9, #4
    rbit w15, w9
    clz w16, w15
    lsr w17, w15, w16
    bic w18, w17, w9
    mov w13, #1
    sub x14, x1, #1
    strb w0, [x14, w13, uxtw]
    mov w13, #-1
    add x14, x1, #1
    ldrb w2, [x14, w13, sxtw]
    add w0, w2, #1
    ret
