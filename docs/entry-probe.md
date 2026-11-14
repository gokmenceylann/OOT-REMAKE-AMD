# rtld giriş testi

```powershell
python -m pip install -r requirements.txt
python lift_rtld.py 'C:\Games\OOT\exefs' entry-local.cpp
cl /nologo /std:c++20 /O2 entry-local.cpp /Fe:entry-local.exe
.\entry-local.exe
```

Sıfır X0/X1 varsayımıyla doğrulanmış NSO text segmentindeki sınırlı giriş yolunu C++20'ye çevirir. İlk BL çağrısını yürütmeden durur. Yerel oyun modülünde çağrı ofseti 0x30, hedef 0x21e0 olarak doğrulandı. Tam yürütme, Horizon ve NVN2 henüz uygulanmadı. Oyun verisinden türetilen C++ veya EXE dosyalarını yayımlama.
