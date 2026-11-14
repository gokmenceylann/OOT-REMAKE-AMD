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
    add v4.16b, v1.16b, v2.16b
    sub v5.4s, v1.4s, v2.4s
    mul v6.4h, v1.4h, v2.4h
    fadd v7.2d, v1.2d, v2.2d
    fmul v8.2s, v1.2s, v2.2s
    fsub v9.2d, v2.2d, v1.2d
    fdiv v10.2d, v2.2d, v1.2d
    add v4.16b, v4.16b, v3.16b
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
