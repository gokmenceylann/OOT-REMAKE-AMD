# AArch64 kontrol akışı

`python a64_analyze.py text.bin --base 0x1000 --entry 0x1000` doğrudan dalları izler ve BL hedeflerini yeni fonksiyon girdileri olarak inceler. BR/BLR adreslerini raporlar. Dolaylı hedefleri ve jump table sınırlarını otomatik çözmez. Fonksiyon üyeliği girişten erişilebilirliğe dayanır. Tail call ve örtüşen fonksiyon ayrımı yapılmaz.

Backend, tamsayı LDP/STP için immediate offset, pre-index ve post-index adresleme ile MOVK ve immediate LSL/LSR/ASR biçimlerini destekler. SIMD, FP, register-indexed addressing ve Horizon çağrıları henüz yoktur.
