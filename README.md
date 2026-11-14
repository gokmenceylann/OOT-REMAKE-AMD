# OOT Remake AMD

Windows x64 statik yeniden derleme projesi. Oyun çalıştırma hattı sabitlenmiş Mako kaynaklarıyla yerelde derlenir. Depodaki NSO, AArch64 ve RTLD test araçları bu çalışma ortamından ayrı kullanılabilir.

## Doğrudan Windows derlemesi

Oyun derlemesi için Hookshot tabanlı Mako çalışma ortamı bir alt modüle sabitlenmiştir. Bu hat AArch64 lifting, Horizon ve NVN2/Vulkan kodunu AMD düzeltmeleriyle birlikte kullanır. Yerel oyunu derlemek için [derleme ve lisans rehberine](docs/mako-build.md) bak.

Aşağıdaki bağımsız araştırma araçları, NSO ve AArch64 davranışlarını ayrı ayrı sınamak içindir.

## Yerel ExeFS

```powershell
python -m pip install -r requirements.txt
python inspect_exefs.py 'C:\Games\OOT\exefs'
python verify_exefs.py 'C:\Games\OOT\exefs'
python map_exefs.py 'C:\Games\OOT\exefs'
python link_exefs.py 'C:\Games\OOT\exefs'
```

Bu komutlar sırasıyla NSO sınırlarını kontrol eder, düz/LZ4 segmentlerinin hash'lerini doğrular, BSS ile birlikte belleğe eşleyip RELR/RELA uygular ve modüller arası ABS64, GLOB_DAT, JUMP_SLOT sembollerini çözer. Kaynak oyun dosyalarına yazılmaz.

## AArch64 ve RTLD

`a64_compile.py` Capstone komutlarını tipli IR'ye çevirir. C++20 çıktısı `a64_state.hpp` ile X0–X30, SP, NZCV ve sınır denetimli belleği kullanır. [Komut kapsamı](docs/a64.md)

```powershell
python lift_rtld.py 'C:\Games\OOT\exefs' entry-local.cpp --host-fill
cl /nologo /std:c++20 /O2 /EHsc entry-local.cpp /Fe:entry-local.exe
.\entry-local.exe
```

Varsayılan RTLD denemesi ilk BL'de durur. `--host-fill` doğrulanmış RTLD revizyonunda ilk yordamı test belleğinde çalıştırıp bir sonraki BL'ye ulaşır. Oyundan üretilen C++ veya EXE dosyaları yerelde kalmalıdır. [RTLD ayrıntıları](docs/entry-probe.md)

## Testler

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tests/differential.py --llvm-bin 'C:\Tools\llvm-mingw\bin'
```

Karşılaştırma testi LLVM ile AArch64 test kodu oluşturur, Unicorn'dan beklenen sonuçları alır ve derlenen x64 çıktısının register, NZCV ve bellek durumunu karşılaştırır.
