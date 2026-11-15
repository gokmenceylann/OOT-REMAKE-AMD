# Üçüncü taraf bileşenler

`UPSTREAM-PROVENANCE.md` kaynak ve ikili kimliklerini,
aşağıdaki kayıt kullanım ve dağıtım sınırlarını tanımlar.
Referans sürüm Mako `b77ac86187330eb7447ac65ab23187baac4600ca`.
Upstream ağaçtan gelen bileşenlerin ayrı Git SHA'sı
doğrulanmadığında sabit Mako ağacı ve lisans yolu kullanılır.

| Bileşen | Kaynak / sürüm | Kullanım ve lisans kaydı |
| --- | --- | --- |
| Mako, Hookshot ve Linux/Windows host kaynakları | Sabit Mako gitlink'i. Hookshot/Longshot ilişkisi kaynak kaydında. | Kaynaktan derleme. GPL-3.0-or-later bildirimleri ve dosya başlıkları korunur. |
| Longshot | `Recomper/Longshot@fa2cc03aa5c2369dea53856d4b11bdb9d0299b3b` | Salt kaynak referansı. Depoda GPLv3 lisansı var. Hazır Longshot EXE, DLL, launcher, updater veya shader cache alınmadı. |
| AArch64 yardımcıları | `third_party/a64-kit`, `nx2/` | Kaynaktan. `third_party/a64-kit/NOTICE.TOTKPort.md` ve ilgili kaynak başlıkları korunur. |
| Shader recompiler ve SPIR-V üretimi | `gpu/vk/eden`, `gpu/vk/sirit`, ortak `gpu/third_party/suyu` başlıkları | Kaynaktan. Dosya ve alt bileşen lisansları geçerli. Vulkan hedefinde Eden SPIR-V backend'i ve sirit kullanılır. |
| Vulkan-Headers, SPIRV-Headers, VMA | Baseline build logu sırasıyla `v1.4.345`, `vulkan-sdk-1.4.341.0`, `v3.3.0` gösteriyor. | Build girdileri. Khronos ve VMA bileşenlerinin resmi lisans dosyaları korunur. |
| ImGui, Opus, zstd, SDL2, zbic | Sabit Mako `third_party/` ağacı | Build seçeneklerine göre vendored kaynak veya kütüphane. Sırasıyla `imgui/LICENSE.txt`, `opus/COPYING`, `zstd/LICENSE`, `sdl2/LICENSE.txt`, `zbic/LICENSE`. Windows baseline import tablosunda SDL2/SDL3 DLL'i görülmedi. |
| Kenney input varlıkları ve prompt araçları | `third_party/kenney_input*`, `nx2/prompt_requirements.txt` | Paket kapsamına göre `License.txt` bildirimlerini koru. Üretilen prompt dosyaları ayrıca incelenir. |
| FidelityFX FSR 3.1 kaynakları ve API başlıkları | `third_party/fidelityfx-sdk/LICENSE.txt`, `third_party/fidelityfx/LICENSE.md` | Yerleşik FSR 3.1 ve SDK arayüzü. SDK binary lisansıyla ayrı değerlendirilir. |
| AMD FSR SDK 2.4.0 runtime | `amd_fidelityfx_loader_vk.dll`, `amd_fidelityfx_upscaler_vk.dll` | Kullanıcı AMD'den temin eder. Oyun testi provider 4.1.2'yi doğruladı. Proje paketi bu DLL'leri içermez. |
| Python bağımlılıkları | Mako `requirements.txt`: lz4 4.4.5, NumPy 2.5.4, Capstone 5.0.9, Unicorn 2.1.4, zstandard 0.25.0 ve prompt gereksinimleri | Build/test girdileri. Lisansları ilgili paket ve alt bağımlılıklardan alınır. Oyunun dağıtım paketine Python ortamı eklenmez. |
| LLVM/MinGW ve Windows DLL'leri | Baseline build toolchain ve PE importları | Derleyici araçları yerel. Windows 11 kendi UCRT/Media Foundation ve sistem bileşenlerini sağlar. Vulkan loader/driver sistemden yüklenir. PE importları dinamik yüklemelerin tam listesi değildir. |
| Inno Setup | Kararlı araç paketi ve rc.3 installer için 6.7.3 | Harici paketleme aracı. Kurucu ve portable paket kendi allowlist'ini kullanır. |
| Oyun EXE'si, Vulkan DLL, image.bin, RomFS | Yerel Mako build veya doğrulanmış kararlı runtime | Kullanıcının yerel dosyaları. Bu dal veya GitHub varlığı içinde yer almaz. |

Bu kayıt kaynak ağacı ve mevcut build kanıtıyla hazırlanmış
bir envanterdir. Bir runtime dağıtımı düşünülürse o **somut**
derlemenin bağlantı listesi, dinamik yüklemeleri ve transitive
lisansları ayrıca doğrulanır. GPL kapsamındaki değişiklikler ve
karşılık gelen kaynak korunur. Lisansı veya yeniden dağıtım
hakkı doğrulanamayan hazır ikili paket girdisi olamaz.

- [Mako lisansı](https://github.com/Shakoquo/Mako/blob/b77ac86187330eb7447ac65ab23187baac4600ca/LICENSE)
- [Mako bağımlılık kaynakları](https://github.com/Shakoquo/Mako/tree/b77ac86187330eb7447ac65ab23187baac4600ca/third_party)
- [Longshot lisansı](https://github.com/Recomper/Longshot/blob/fa2cc03aa5c2369dea53856d4b11bdb9d0299b3b/LICENSE)
- [AMD FSR SDK ve runtime dosyaları](https://gpuopen.com/amd-fsr-sdk/)
