.text
.global fixture
fixture:
    str x30, [sp]
    subs w0, w0, #1
    b.eq zero
    bl nested
    ldr x30, [sp]
    ret
zero:
    mov w0, #42
    ret
nested:
    strb w0, [x1]
    ldrb w2, [x1]
    add w0, w2, #1
    ret
