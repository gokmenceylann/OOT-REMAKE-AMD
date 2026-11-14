# AMD FSR Upscaling 4.1.2 (Windows Vulkan)

1. Initialize the pinned Mako submodule and follow the [Windows build guide](mako-build.md). Pass `-EnableFsr412` to the build script. It applies the GPL-3.0-or-later renderer patch to the local submodule.
2. Obtain the signed **Vulkan** loader and upscaler DLLs from AMD's [FSR SDK v2.4.0](https://github.com/GPUOpen-LibrariesAndSDKs/FidelityFX-SDK/tree/v2.4.0/Kits/FidelityFX/signedbin): `amd_fidelityfx_loader_vk.dll` and `amd_fidelityfx_upscaler_vk.dll`. Keep the [SDK license](https://github.com/GPUOpen-LibrariesAndSDKs/FidelityFX-SDK/blob/v2.4.0/Kits/FidelityFX/docs/license.md) with the DLLs. Set `RX_VK_FSR_DIR` to their absolute folder, or place them next to the game executable. AMD binaries and game-derived files stay local.
3. Run the game directly. In Graphics, select AMD FSR 4 and Quality, Balanced, or Performance. The adjacent AMD FSR 4 Native AA choice renders at full scale. Existing graphics settings and mode IDs are reused.

The SDK enumerates providers using the real Vulkan device and pins the exact 4.1.2 version ID on Windows. The renderer checks the created context's provider ID and queries its input requirements. The existing temporal path supplies scene color, depth, pixel-space motion vectors and jitter. A single reused R32F texel supplies unity exposure for the tonemapped scene. A provider requiring masks this path cannot supply is rejected. Output resolution and maximum context resolution use the scene target. Per-frame render resolution is passed separately. No mask targets are allocated for optional inputs.

The log distinguishes provider enumeration, context creation, and successful dispatch. Only `FSR provider dispatched` confirms a successful ML dispatch. When unavailable, the existing FSR 3.1 path is selected, with the game's scaler remaining available when that path cannot run. `RX_VK_FSR4=0` and `RX_VK_FSR=1` can exercise the built-in FSR 3.1 path.

[AMD SDK 2.4.0 integration and provider versioning](https://gpuopen.com/learn/amd-fsr-sdk-2-4-rx-6000-ryzen-apus/)

## Türkçe

Yerel derlemede `-EnableFsr412` kullan. AMD’nin yukarıda bağlantısı verilen FSR SDK 2.4.0 paketinden imzalı Vulkan loader ve upscaler DLL’lerini edin. SDK lisansını koru. DLL’leri `hookshot.exe` yanına koy veya `RX_VK_FSR_DIR` ile dizini belirt.

Graphics menüsünden AMD FSR 4 ve çözünürlük modunu seç. FSR ölçekleme mevcut oyun karesini yeniden oluşturur. Frame Generation ek kare üretir ve ayrı bir ayardır. Logdaki `FSR provider dispatched: 4.1.2` satırı başarılı ML dispatch’i doğrular. `upscalers … using 4.1.2` yalnızca seçim kaydıdır. Context hatasında FSR 3.1 fallback ve [context tanılama rehberine](fsr-context-recovery.md) bak.
