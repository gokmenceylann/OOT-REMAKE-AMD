
`a64_compile.py` Capstone komutlarını tipli IR'ye çevirir. C++20 çıktısı `a64_state.hpp` ile X0–X30, SP, NZCV ve sınır denetimli belleği kullanır. [Komut kapsamı](a64.md)

```powershell
python lift_rtld.py 'C:\Games\OOT\exefs' entry-local.cpp --host-fill
cl /nologo /std:c++20 /O2 /EHsc entry-local.cpp /Fe:entry-local.exe
.\entry-local.exe
```

Varsayılan RTLD denemesi ilk BL'de durur. `--host-fill` doğrulanmış RTLD revizyonunda ilk yordamı test belleğinde çalıştırıp bir sonraki BL'ye ulaşır. Oyundan üretilen C++ veya EXE dosyaları yerelde kalmalıdır. [RTLD ayrıntıları](docs/entry-probe.md)
