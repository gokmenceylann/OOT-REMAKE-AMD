# OOT Remake AMD

Windows x64 için yerel statik yeniden derleme projesi. Oyun, sabitlenmiş Hookshot tabanlı Mako kaynakları ve kullanıcının yerel ExeFS/RomFS dosyalarıyla derlenir. Çıktıdaki oyun EXE’si doğrudan açılır.

## Oyunu yerelde derle

```powershell
git clone --recurse-submodules https://github.com/gokmenceylann/OOT-REMAKE-AMD.git
cd OOT-REMAKE-AMD
```

Python, llvm-mingw ve Vulkan derleme bağımlılıklarını hazırlayıp `scripts/Build-LocalGame.ps1` komutunu çalıştır. Girdi yollarını ve derleme klasörünü komuta ver. [Windows kurulum, derleme ve lisans rehberi](docs/mako-build.md)

## Doğrulama durumu

Yerel Mako 4.1 derlemesi tamamlandı. Oyun işlemi açıldı, AMD Vulkan sürücüsünü yükledi ve ilk 60 saniyelik kayıtta **28,82 Present FPS** ortalaması verdi. Oyun sahnesi, fiziksel GPU seçimi, kararlı 60 FPS ve FSR bu ölçümde doğrulanmadı. [Ölçüm koşulları ve sonuçları](docs/validation-rx6700m.md)

## Depo yapısı

- `scripts/Build-LocalGame.ps1` yerel Windows derlemesini başlatır.
- `upstream/mako/` sabitlenmiş Mako kaynak alt modülüdür.
- `docs/` derleme, lisans ve RX 6700M ölçüm bilgilerini içerir.

Oyun dökümleri, ExeFS/RomFS, anahtarlar, oyun verisinden üretilen kod, EXE/DLL ve shader önbellekleri yerelde tutulur. [Kaynak ve lisans bilgisi](docs/mako-build.md#kaynak-ve-lisans)
