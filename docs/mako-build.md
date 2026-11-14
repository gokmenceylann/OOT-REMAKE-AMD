# Mako kaynaklarından yerel Windows derlemesi

Mako, Hookshot'ın AArch64 dönüştürme ve derleme altyapısını, Horizon host uygulamalarını, NVN2 ve Vulkan çizicisini, ayrıca Mako'nun AMD değişikliklerini birlikte taşır. Kaynak bağımlılığı `bef2014454a9a3e669c77cb4e6cfb4b04f362f3a` commit'ine sabitlendi. Doğrudan derlenen oyun EXE'si kullanılır.

~~~powershell
git clone --recurse-submodules https://github.com/gokmenceylann/OOT-REMAKE-AMD.git
cd OOT-REMAKE-AMD
& 'C:\Tools\Python\python.exe' -m pip install -r upstream/mako/requirements.txt

.\scripts\Build-LocalGame.ps1 `
    -ExeFS 'D:\Game\exefs' -RomFS 'D:\Game\romfs' `
    -LocalRoot 'D:\OOT-local' -Python 'C:\Tools\Python\python.exe' `
    -LlvmMingw 'C:\Tools\llvm-mingw' -Cpm 'C:\Tools\cpm'
~~~

Python ortamında `python -m pip install -r upstream/mako/requirements.txt` ile tanımlanan üst proje derleme gereksinimleri, CPM önbelleğinde Vulkan-Headers, SPIRV-Headers ve VulkanMemoryAllocator bulunmalıdır. Derleme tamamlandığında dosyayı build kökündeki `game` klasöründen çalıştır. Komuttaki dosya yolları örnektir. Derleme çıktısını kaynak deposu dışında tut.

~~~powershell
Set-Location 'D:\OOT-local\game'
.\hookshot.exe
~~~

[İlk yerel ölçüm](validation-rx6700m.md)

## Kaynak ve lisans

Bu depo upstream kaynaklarını kopyalamak yerine Git submodule ile sabitler. Mako ve devraldığı Hookshot kodu için upstream GPL-3.0-or-later lisansı ile dosya başlıkları korunur. Üçüncü taraf bileşenlerin kendi bildirimleri ve lisansları upstream ağacında geçerlidir. AMD veya NVIDIA SDK ikilileri bu depoda dağıtılmaz. Oyun verisi, çevrilmiş C, oyun EXE/DLL dosyaları, imajlar ve oyundan türetilmiş shader cache'leri paylaşılmaz.

- [Sabitlenen Mako kaynak ağacı](https://github.com/Shakoquo/Mako/tree/bef2014454a9a3e669c77cb4e6cfb4b04f362f3a)
- [Mako lisansı](https://github.com/Shakoquo/Mako/blob/bef2014454a9a3e669c77cb4e6cfb4b04f362f3a/LICENSE)
- [Hookshot/Mako kaynak ve üçüncü taraf geçmişi](https://github.com/Shakoquo/Mako/blob/bef2014454a9a3e669c77cb4e6cfb4b04f362f3a/docs/design.md)
