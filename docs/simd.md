# AArch64 SIMD ve FP

128 bit AND/ORR/EOR ile desteklenen tamsayı lane düzenlerinde ADD, SUB ve MUL uygulanır. Skaler S/D ve 2S, 4S, 2D vektör biçimlerinde FADD, FSUB, FMUL ve FDIV vardır. Dar yazımlar üst bitleri sıfırlar.

MRS/MSR, FPCR ve FPSR için maskelenmiş register erişimi sağlar. FP aritmetiği FPCR sıfırken varsayılan host kayan nokta ortamında çalışır. FPCR sıfır dışında ise işlem `unsupported_fp_mode` ile durur. FPSR istisna bayrakları aritmetikten üretilmez. NaN yayılımı, konuk yuvarlama kipleri ve özel istisna semantiği doğrulanmadı.

`python tests/differential.py --llvm-bin C:\Tools\llvm-mingw\bin` normal aritmetiği Unicorn ile karşılaştırır ve FP register erişimini ayrıca sınar.
