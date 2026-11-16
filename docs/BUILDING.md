# Build and run on Windows

Use Windows 11 x64, Git and the Python, LLVM MinGW and CPM dependencies for the pinned Mako revision. CPM must contain Vulkan-Headers v1.4.345, SPIRV-Headers vulkan-sdk-1.4.341.0 and VulkanMemoryAllocator v3.3.0 for the documented Vulkan build. Use a Vulkan-compatible driver, compatible local ExeFS and RomFS, and disk space for generated sources and outputs.

~~~powershell
git clone --branch performance/stable-mako-411 --recurse-submodules https://github.com/gokmenceylann/OOT-REMAKE-AMD.git
Set-Location OOT-REMAKE-AMD
& 'C:\Tools\Python\python.exe' -m pip install -r upstream/mako/requirements.txt
.\scripts\Build-LocalGame.ps1 -ExeFS 'D:\Game\exefs' -RomFS 'D:\Game\romfs' -LocalRoot 'D:\OOT-local' -Python 'C:\Tools\Python\python.exe' -LlvmMingw 'C:\Tools\llvm-mingw' -Cpm 'C:\Tools\cpm' -EnableFsr412 -EnableMemoryOptimization
Set-Location 'D:\OOT-local\game'
.\hookshot.exe
~~~

Paths are examples. Keep a clean checkout for each patch set. The local build script applies patches to the pinned submodule and writes output under `LocalRoot`. Record the project SHA, submodule SHA, enabled patches and runtime hashes for your report.

Published installers use exact runtime hashes and import already-built files. A rebuild may produce different hashes. Run a compatible local rebuild from its output folder, and use the installer only with the pair specified in its manifest. See [install options](install.md), [rc.4 installation](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.2.0-rc.4/docs/install-v0.2.0-rc.4.md) and [FSR dependencies](fsr-4.1.2.md).
