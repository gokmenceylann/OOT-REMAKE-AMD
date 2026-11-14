# rtld giriş testi

```powershell
python -m pip install -r requirements.txt
python lift_rtld.py 'C:\Games\OOT\exefs' entry-local.cpp --host-fill
cl /nologo /std:c++20 /O2 /EHsc entry-local.cpp /Fe:entry-local.exe
.\entry-local.exe
```

Test X0 ve X1 için sıfır giriş varsayar. Varsayılan mod ilk BL öncesinde durur. `--host-fill`, doğrulanmış rtld text hash'i ve 0x30 → 0x21e0 çağrısı için sınır denetimli host memset çalıştırır. Bellek bir test tamponudur. Laptopta 264 bayt yazdı ve 0x48 → 0x100 çağrısında durdu.

Oyun başlatma, Horizon servisleri, NVN2 çizimi ve FSR bu testte uygulanmış değildir. Oyun verisinden türetilen C++ ve EXE dosyalarını yayımlama.
