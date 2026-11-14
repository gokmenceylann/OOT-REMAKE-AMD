.text
.global fixture
fixture:
    stp x30, xzr, [sp, #-16]!
    subs w0, w0, #1
    b.eq zero
    bl nested
    ldp x30, xzr, [sp], #16
    ret
zero:
    ldp x30, xzr, [sp], #16
    mov w0, #42
    ret
nested:
    mov w9, #0x1234
    movk w9, #0xabcd, lsl #16
    lsl w10, w9, #1
    lsr w11, w10, #3
    asr w12, w9, #4
    strb w0, [x1]
    ldrb w2, [x1]
    add w0, w2, #1
    ret
