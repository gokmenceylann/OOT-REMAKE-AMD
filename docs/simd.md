# AArch64 vektör aritmetiği

ADD/SUB desteklenen tamsayı lane düzenlerinde çalışır. MUL, 8/16/32 bit lane kullanır. FADD, FSUB, FMUL ve FDIV 2S, 4S ve 2D düzenlerinde çalışır. Dar vektör yazımları üst 64 biti sıfırlar ve hedef operandla aynı register olsa da kaynak lane'ler korunur. FPCR/FPSR ve özel NaN/istisna davranışları uygulanmadı. Genel FP doğruluğu için host ve konuk FP durumlarının karşılaştırılması gerekir.

`python tests/differential.py --llvm-bin C:\Tools\llvm-mingw\bin` AArch64 ve yerel C++ yürütümünün vektör register'larını da karşılaştırır.
