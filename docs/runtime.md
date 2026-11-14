# RTLD yordamı ve Windows ABI

```powershell
python run_rtld.py 'C:\Games\OOT\exefs\rtld' --clang 'C:\Tools\llvm-mingw\bin\clang++.exe'
```

Bu komut doğrulanmış RTLD sürümünde 0x100 yordamını yerel x64 koduna çevirir, NSO segmentlerini ve BSS'yi düz misafir belleğine eşler ve yordamı çağırır. Geçici dosyalara yazılan oyun türevi kod ve bellek yalnızca yerelde kalır. Yordam kendi relocation işlemlerini yaptığı için başlangıç belleği orijinal segment baytlarını kullanır. Windows x64 testinde 0x800004a0 adresindeki dönüşe ulaşıldı. Bu bir yordam çağrısıdır ve tam oyunu çalıştırmaz.

Analiz, doğrudan çağrılara ek olarak komşu ADR → BR/BLR desenlerini aday olarak izler. Gerçek hedef çalışma anında derlenmiş adres tablosunda doğrulanır. Genel register veri akışı ve jump table keşfi kapsam dışıdır.

HostBinding tablosu dört tamsayı argümanı ve bir tamsayı dönüşü olan kayıtlı host işlevlerini destekler. C++ derleyicisi Windows x64 ABI çağrısını oluşturur. FP, pointer ve değişken argümanlı ABI köprüleri kapsam dışıdır.

SIMD/FP kapsamı 128 bit AND/ORR/EOR ve varsayılan host FP ortamındaki skaler FADD/FSUB/FMUL/FDIV ile sınırlıdır. FPCR ve FPSR davranışı uygulanmadı. Altı Unicorn karşılaştırması ve kayıtlı host çağrısı testi yerelde geçti.
