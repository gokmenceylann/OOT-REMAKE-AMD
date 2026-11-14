# AArch64 kontrol akışı

`python a64_analyze.py text.bin --base 0x1000 --entry 0x1000` doğrudan dalları izler, BL hedeflerini inceler ve BR/BLR adreslerini raporlar.

```powershell
python compile_nso.py 'C:\Games\OOT\exefs\rtld' rtld-local.cpp --offset 0x100
cl /nologo /std:c++20 /O2 /c /I. rtld-local.cpp
```

Derleyici, belirtilen girişe ve doğrudan çağrılara erişilebilir komutları üretir. BR/BLR, derlenmiş konumlara çalışma anında yönlenebilir. Gerekli dolaylı hedefleri `--target-offset` ile ekle. Jump table hedefleri otomatik çıkarılmaz. Çıktı nesne dosyası kendi başına NSO yürütmez. Bellek eşleme ve çağrı başlatma bilgisi bir üst katmandan sağlanmalıdır.

Desteklenen tamsayı biçimlerine register-offset yükleme/saklama, index genişletme, register shift, CLZ, RBIT, BIC/BICS, TBZ/TBNZ, MADD/MSUB ve NEG eklendi. SIMD/FP, Horizon ve NVN2 yürütümü açık kalıyor.
