# Installation

1. Install a Vulkan-capable Windows GPU driver. Get Git, Python, llvm-mingw and the header dependencies in the [build guide](mako-build.md). Close the game before updates.
2. Clone the source with submodules. Prepare your own matching game ExeFS and RomFS directories. Keep them outside the repository. The build script accepts extracted directories. Use paths you control and can read.
3. Run [Build-LocalGame.ps1](mako-build.md) with those paths and an external local build root. Enable FSR 4.1.2 with `-EnableFsr412`; enable Radeon memory changes with `-EnableMemoryOptimization`. The output is `<LocalRoot>\game`.
4. The game directory should contain `hookshot.exe`, `hookshot_vk.dll`, the generated `image.bin` and a `romfs` directory. Run `Test-LocalGame.ps1 -GameDirectory 'D:\OOT-local\game'` from the tools or source package. The check identifies missing files without starting the game.
5. Open `hookshot.exe` directly from the game folder. The first build skips optional advance shader preparation. Pipelines can compile on first use; retain the caches for subsequent runs.

## Updates and saves

Back up `game/user/save/` and `game/hookshot_options.ini` before updating. Build again with the same `LocalRoot` to retain the established game folder and cache files. Cache compatibility depends on the renderer and shader stamp. Save paths differ if you launch with a custom `--user` directory. The tools installer has its own installation directory and uninstalls its own payload.

## Türkçe

1. Vulkan destekli GPU sürücüsünü kur. Git, Python, llvm-mingw ve CPM başlıklarını [derleme rehberine](mako-build.md) göre hazırla.
2. Depoyu alt modülleriyle klonla. Kendi uyumlu ExeFS ve RomFS dizinlerini depo dışında tut. Derleme komutuna bu iki dizini ve yerel çıktı kökünü ver.
3. `<LocalRoot>\game` içinde `hookshot.exe`, `hookshot_vk.dll`, `image.bin` ve `romfs` bulunmalı. `Test-LocalGame.ps1 -GameDirectory 'D:\OOT-local\game'` ile dosyaları kontrol et.
4. `hookshot.exe` dosyasını doğrudan aç. Shader ve pipeline önbellekleri kullanım sırasında oluşturulabilir. Güncellemeden önce `user/save/` ve `hookshot_options.ini` dosyasını yedekle. Aynı `LocalRoot` ile derleyerek mevcut oyun klasörünü kullan.

## Windows x64 game import preview

On Windows 11 x64, choose a new game directory and a completed Mako build
from your own copy of the game. The source folder must contain matching
`hookshot.exe`, `hookshot_vk.dll`, `image.bin` and `romfs/`. A build
can be prepared locally with the source instructions above. Install then open
`hookshot.exe` directly in the destination. The destination can already
contain `user/save/` and `hookshot_options.ini`, which Setup preserves.
Uninstall removes installer-managed runtime files and shortcuts. It leaves
the supplied game data, saves and settings in place.

For the portable ZIP, extract it and use Windows PowerShell:

~~~powershell
.\scripts\Import-LocalGame.ps1 -GameDirectory 'D:\MyLocalBuild\game' -Destination 'D:\MyPortableGame'
~~~

The pinned Windows build imports the Windows Universal CRT and Media
Foundation. Windows 11 includes the Universal CRT. Install the Media
Feature Pack for Windows 11 N if `mfplat.dll` is missing. Install a Vulkan
GPU driver. The inspected llvm-mingw EXE and DLL had no Visual C++ Redistributable
imports. A different build may have different runtime requirements.

FSR 4 is optional. Obtain the AMD SDK yourself and follow the separate
[FSR 4.1.2 instructions](fsr-4.1.2.md). Use your own copy of the runtime DLLs
if the compatible provider is available. Otherwise select FSR 3.1 or Game
scaler. The installer accepts a complete user-supplied build with the AMD
DLLs absent. Runtime fallback behavior depends on the installed renderer.

Nintendo game code is baked into the local EXE during recompilation.
Public archives contain only installer code, support scripts and documentation.
An extracted game dump by itself is insufficient for this import workflow.

## Windows x64 aktarım önizlemesi

Windows 11 x64 üzerinde yeni bir hedef klasör ile kendi oyun kopyanızdan
hazırladığınız yerel Mako derlemesini seçin. Kaynak klasörde birbiriyle uyumlu
`hookshot.exe`, `hookshot_vk.dll`, `image.bin` ve `romfs/` bulunmalı.
Hedef bilgisayarda derleyici gerekmez. Kurulumdan sonra EXE doğrudan açılır.
Hedefteki `user/save/` ve `hookshot_options.ini` korunur. Kaldırma aracı
programı ve kısayolu kaldırır, save, ayarlar ve oyun verisini bırakır.
Portable ZIP için yukarıdaki PowerShell komutu kullanılabilir.
