.text
    msr fpsr, x0
    mrs x2, fpsr
    msr fpcr, x1
    mrs x3, fpcr
    fadd s0, s0, s0
    ret
