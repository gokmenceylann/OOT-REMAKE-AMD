# Mako kaynaklarından yerel Windows derlemesi

Mako, Hookshot'ın AArch64 dönüştürme ve derleme altyapısını, Horizon host uygulamalarını, NVN2 ve Vulkan çizicisini, ayrıca Mako'nun AMD değişikliklerini birlikte taşır. Kaynak bağımlılığı `b77ac86187330eb7447ac65ab23187baac4600ca` commit'ine sabitlendi. Doğrudan derlenen oyun EXE'si kullanılır.

~~~powershell
git clone --recurse-submodules https://github.com/gokmenceylann/OOT-REMAKE-AMD.git
cd OOT-REMAKE-AMD
& 'C:\Tools\Python\python.exe' -m pip install -r upstream/mako/requirements.txt

.\scripts\Build-LocalGame.ps1 `
    -ExeFS 'D:\Game\exefs' -RomFS 'D:\Game\romfs' `
    -LocalRoot 'D:\OOT-local' -Python 'C:\Tools\Python\python.exe' `
    -LlvmMingw 'C:\Tools\llvm-mingw' -Cpm 'C:\Tools\cpm' -EnableFsr412 -EnableMemoryOptimization
~~~

Python ortamında `python -m pip install -r upstream/mako/requirements.txt` ile tanımlanan üst proje derleme gereksinimleri, CPM önbelleğinde Vulkan-Headers, SPIRV-Headers ve VulkanMemoryAllocator bulunmalıdır. Derleme tamamlandığında dosyayı build kökündeki `game` klasöründen çalıştır. Komuttaki dosya yolları örnektir. Derleme çıktısını kaynak deposu dışında tut.

~~~powershell
Set-Location 'D:\OOT-local\game'
.\hookshot.exe
~~~

[İlk yerel ölçüm](validation-rx6700m.md)

## Kaynak ve lisans

Bu depo upstream kaynaklarını kopyalamak yerine Git submodule ile sabitler. Mako ve devraldığı Hookshot kodu için upstream GPL-3.0-or-later lisansı ile dosya başlıkları korunur. Üçüncü taraf bileşenlerin kendi bildirimleri ve lisansları upstream ağacında geçerlidir. AMD veya NVIDIA SDK ikilileri bu depoda dağıtılmaz. Oyun verisi, çevrilmiş C, oyun EXE/DLL dosyaları, imajlar ve oyundan türetilmiş shader cache'leri paylaşılmaz.

- [Sabitlenen Mako kaynak ağacı](https://github.com/Shakoquo/Mako/tree/b77ac86187330eb7447ac65ab23187baac4600ca)
- [Mako lisansı](https://github.com/Shakoquo/Mako/blob/b77ac86187330eb7447ac65ab23187baac4600ca/LICENSE)
- [Hookshot/Mako kaynak ve üçüncü taraf geçmişi](https://github.com/Shakoquo/Mako/blob/b77ac86187330eb7447ac65ab23187baac4600ca/docs/design.md)

## Mako 4.1.1

Mako 4.1.1 uses Vulkan renderer API 23. Deploy the matching EXE and Vulkan DLL
together. Keep user settings and saves. On first launch Mako moves the older
cache files to cache/ and logs to logs/. Its shader translator changed, so
some effects and caches can be rebuilt on first launch. Let the program
validate their stamps.

The RX 6700M patches retain the FSR provider and dispatch checks, runtime
fallback, Vulkan allocation telemetry, and Windows pipeline cache commit
guard. Shader cache migration and image retirement follow Mako 4.1.1.

[Official Mako 4.1.1 release notes](https://github.com/Shakoquo/Mako/releases/tag/mako-4.1.1)
