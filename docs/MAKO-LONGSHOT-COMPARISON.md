# Mako 4.1.1 ve Longshot karşılaştırması

## 1. Stabil Mako temel commit SHA

OOT v0.1.5 ve dal başlangıcı
`93e7586cf57f65260b4bab3cde1eecb3d28573bc`.
Mako `b77ac86187330eb7447ac65ab23187baac4600ca`.
SHA-256 değerleri ve karşılaştırılan main
[upstream kaydında](UPSTREAM-PROVENANCE.md).

## 2. Longshot güncel commit SHA

`fa2cc03aa5c2369dea53856d4b11bdb9d0299b3b`, main.
Aşağıda belirtilen eski işlerin kaynak sürümü, aksi
belirtilmedikçe bu HEAD'in ebeveyni
`9447e1de5e01ffab15a179ab4b55a1320fe14231` içindeki
Hookshot geçmişidir. [Longshot kaynak ağacı](https://github.com/Recomper/Longshot/tree/fa2cc03aa5c2369dea53856d4b11bdb9d0299b3b)

## 3. Ortak upstream ve proje kökeni

Longshot'un HEAD ebeveyni Mako gitlink'inin atasıdır.
Mako merge'leri ve yerel OOT yamaları ayrışmayı açıklar.
Recomp ailesi Hookshot kökenli ortak AArch64, Horizon ve NVN
katmanlarını kullanır. OOT'un doğrudan ana kökü Mako 4.1.1.
[Kaynak ağacı ve commit zinciri](UPSTREAM-PROVENANCE.md)

## 4. İki projenin mimari farkları

| Alan | Kaynak, iş ve kategori | Bağımlılık, aktarım ve RX 6700M riski |
| --- | --- | --- |
| AArch64 kod üretimi | `nx2/lift.py::main`, `nx2/lifted_c.py`, `nx2/build.py::compile_one`. `3fa63001` sayfa işaretlerini gruplar. Mako'da mevcut, lifter sonradan farklılaşmış. | A64 kit, üretilen C, linker ve guest memory aynı sözleşmeyi kullanır. Sadece ölçülmüş düzeltme seçilmeli. 5800H derleme veya frame kazancı ölçülmedi. Yüksek risk. [Commit](https://github.com/Recomper/Longshot/commit/3fa63001) |
| Horizon ve CPU runtime | `host/hos_svc.c::a64_svc`, `hos_thread.c`, `hos_mem.c`. `428633a9` çekirdek topolojisi kuralı Mako geçmişinde. İki implementasyonun thread varsayılanları farklı. | Scheduler, page tracking ve host çağrıları birlikte çalışır. X3D topolojisi ölçümleri 5800H'a aktarılmaz. Save/yükleme ve geçiş testleri gerekir. Yüksek risk. [Commit](https://github.com/Recomper/Longshot/commit/428633a9) |
| NVN2 ve replay | `host/nvn_native.c::nvnQueueSubmitCommands`, `nvnQueueFenceSync`, `gpu/vk/vk_replay.cpp`. `ca50be6a` inline replay'de sanal çekirdeği bırakır. Ortak yapı mevcut; renderer API 14 ve 23 doğrudan taşınamaz. | Host/renderer struct, recording ve fence sahipliği birlikte kalır. DLL değişimiyle RX 6700M kazanımı beklenmez. Yüksek risk. [Commit](https://github.com/Recomper/Longshot/commit/ca50be6a) |
| Shader, mesh ve culling | `vk_shader.cpp`, `gpu/vk/eden`, `gpu/vk/sirit`, `vk_draw.cpp` içindeki `vkCmdDrawMeshTasks*EXT` ve mesh fallback. `39d978b49f` AMD ASTC/resolve işi Mako'da mevcut. Shader implementasyonları ayrışmış. | SPIR-V, descriptor ve fallback kaynak düzeni bir bütündür. Cache stamp, geometri ve AMD driver compile testleri gerektirir. Yüksek risk. [Commit](https://github.com/Recomper/Longshot/commit/39d978b49f) |
| Pipeline cache ve worker | `vk_draw.cpp::graphics_pipeline`, `precompile_run`, `vk_jobs.cpp::jobs_wait`. `16c42ef06c` başarısız işin durumunu yayımlar. `5e4e2113d8` Longshot listesinde 4.276 kayıt. Her iki commit Mako geçmişinde. | Test uyarlaması düşük risk. Runtime kuyruğu ve cache stamp değişikliği yüksek risk. Longshot'un sıkıştırılmış liste blob'u bu yolda var, aynı yol Mako pin'inde yok. Yerel shipped pipeline dosyasıyla eşdeğerliği kanıtlanmadı. [Worker](https://github.com/Recomper/Longshot/commit/16c42ef06c) · [Liste](https://github.com/Recomper/Longshot/commit/5e4e2113d8) |
| Bellek ve VRAM | `vk_memory.cpp::import_pool`, `vk_texture.cpp::compact_step`, `vk_vma.cpp`. `325583b981` bind rollback ve `393242121a` compaction mevcut. Mako `22b8d22d` late pages ve sparse mirrors varsayılanlarını değiştiriyor. | Import, VMA ve timeline sahipliği korunmalı. Compaction, heap baskısını azaltabilir ve GPU kopya maliyeti ekleyebilir. Eş koşullu ölçüm gerektirir. Yüksek risk. [Bind](https://github.com/Recomper/Longshot/commit/325583b981) · [Compaction](https://github.com/Recomper/Longshot/commit/393242121a) |
| Frame pacing ve FG | `vk_framegen.cpp::framegen_record`, `display_main`, `vk_replay.cpp`. `08f3fe4c` swapchain yedek görüntü sayısı ve present muhasebesini düzeltir. Mako geçmişinde mevcut, ilgili kod daha sonra ayrışmış. | Acquire/present ve semaphore düzeni ayrı doğrulanmalı. FG Off/Auto ölçümleri ve temel/sunulan FPS ayrılmalı. Yüksek risk. [Commit](https://github.com/Recomper/Longshot/commit/08f3fe4c) |
| FSR ve temporal | `vk_fsr3.cpp::fsr3_upscale`, `vk_fsr3fi.cpp`, `vk_fsr4.cpp`, `vk_temporal.cpp::temporal_upscale`. `c8fe4b01`, `2982420d3f`, `8fc2587c7d`, `0cf9936c01` ortak geçmişte. OOT'un 4.1.2 provider yaması yerel fark. | Jitter, motion, history ve SDK yaşam döngüsü birlikte sınanmalı. Longshot 4.1.2 dispatch'i RX 6700M'de doğrulanmadı. Doğrudan taşınamaz, yüksek risk. [FSR 3.1](https://github.com/Recomper/Longshot/commit/c8fe4b01) · [Temporal](https://github.com/Recomper/Longshot/commit/0cf9936c01) |
| Save/load, menü ve ayarlar | `host/nn_fs.c`, `host/hos_main.c` save importu, `host/oot_menu.c`, `vk_menu.cpp`. Ortak backend mevcut. Mako `SAVE FOLDER` ve Hookshot adlarını koruyor. HEAD `fa2cc03a` Longshot adlarını kullanır. | Dosya, hesap ve slot düzeni değişirse gerçek save turu şart. Menü kodunu veya binary'yi devralmak gereksiz ve yüksek riskli. [Kaynak commit](https://github.com/Recomper/Longshot/commit/fa2cc03aa5c2369dea53856d4b11bdb9d0299b3b) |
| Build ve dağıtım | `nx2/build.py::compile_one`, `nx2/make_game.py`, `.github/workflows/release.yml`, `builder/`. `50b68667` updater asset digest kontrolü ortak geçmişte. OOT yerel build ve Inno importer akışı ayrı. | SHA-256 doğrulama ve test yöntemi uyarlanabilir. Launcher, updater ve binary dağıtımını devralmak gereksiz. Belge/test düşük risk. [Commit](https://github.com/Recomper/Longshot/commit/50b68667) |

## 5. Longshot'tan aktarılmaya değer yenilikler

**A — Düşük risk:** Upstream test yöntemlerini ve shader
provenance pratiğini kullan. Worker başarısızlık, import
rollback ve FSR lifetime testlerinin Mako'da var olan
karşılıklarını OOT baseline üzerinde koştur. Test çıktısı
ve kapsanan kod açık olmalı. [Shader provenance](https://github.com/Recomper/Longshot/commit/cf6978b1a5)

**B — Uyarlama:** Ancak eş koşullu ölçümle bir açık
görülürse dar shader, import veya replay düzeltmesi seç.
Pipeline listesinin formatı, oyunun ve shader damgasının
eşleşmesi, ısıtma süresi ve VRAM etkisi doğrulanmalı.
Önce FG Off geçişi, sonra FG Auto. Bir kaynak değişikliği
ve bir A/B hipoteziyle ilerle.

**C — Şimdilik alınmasın:** Longshot renderer binary'si,
launcher/updater, toplu shader ağacı, yeni thread politikası,
önbellek aktarımı ve bellek varsayılanlarının topluca
değiştirilmesi. Aynı çalışma anahtarları ve görüntü doğruluğu
gösterilmeden kayda değer fayda varsayılmaz.

## 6. Mako'dan kesinlikle korunması gereken özellikler

API 23 EXE/DLL eşleşmesi, doğrudan `hookshot.exe`, save/ayar
yolları, mevcut AMD shader/bellek uyumluluğu, kararlı
FSR 4.1.2 provider yaması ve FSR 3.1 fallback. GPU, Vulkan
heap capacity, dinamik budget, VMA ve WDDM sayıları ayrı
karşılaştırılır. 6700M'ye ait heap capacity fiziksel VRAM
olarak etiketlenmez.

## 7. Longshot derlemeleri ve binary bileşenlerinin kaynakları

İncelenen Longshot deposunda GitHub Releases ve Git etiket
sorguları hazır sürüm döndürmedi. Build ve release workflow
kaynakları var. Bu dalda Longshot binary veya kopyalanan
dosya yok. Geçerli paketlerin kaynağı, mevcut OOT/Mako
yerel build veya upstream SDK'dır.
[Longshot Releases](https://github.com/Recomper/Longshot/releases)

## 8. Kullanılacak, uyarlanacak ve kullanılmayacak bileşenler

Mako runtime, lifter ve Vulkan renderer kaynaktan derlenir.
Kullanıcı AMD SDK'yı kendi sistemine ekler. Doğrulanmış ilk
EXE/DLL çifti test referansıdır. Longshot test yöntemi ve
kod geçmişi referans, seçilmiş bir runtime değişikliği ise
sonraki onay ve uyarlama gerektirir. Bağımsız Longshot
runtime veya installer kullanılmaz.

## 9. Lisans ve dağıtım riskleri

Upstream GPL ve bileşen lisansları korunur. Yerel oyun
verileri, oyundan üretilen EXE ve shader cache yayımlanmaz.
AMD SDK ve bilinmeyen binary'ler paket kapsamı dışındadır.
[Bileşen envanteri](THIRD-PARTY-COMPONENTS.md)

## 10. Yeni recomp mimarisi

`OOT baseline → Mako lifter ve Horizon host → NVN2 replay
→ API 23 Vulkan renderer → AMD FSR ve bellek politikası`.
Her tasarım değişikliği ayrı patch veya dar commit olarak
izlenir. Build ve test araçları ayrı çalışır. Yeni dalın
sürüm geçmişi OOT v0.1.5 ve mevcut ön yayınlardan ayrı tutulur.

## 11. İlk aktarım için önerilen değişiklik

Runtime değişikliğinden önce, pipeline job-failure ve
Vulkan import rollback testlerini kararlı build zincirine
bağla. Bunlar zaten Mako'da bulunan davranışları
karakterize eder. İlk performans adayını sadece bu testler
ve aynı save/cache ile Castle Town FG Off ölçümü sonrasında
seç. Önceki kısmi referansta 30 FPS sağlanmadı ve sabit
sahne aralığında pipeline beklemesinden çok bellek
eşitlemesi görüldü.
[Mevcut donanım referansı](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/36a1a3d/docs/mako-411-baseline-validation.md)

## 12. Test ve sürüm planı

- Kaynak pin, patch listesi, EXE/DLL ABI ve SHA-256 her
  adayda doğrulanır. İlk testler oyunsuz kaynak testleridir.
- Windows x64 staging, aynı save ve aynı başlangıç cache
  kopyasını kullanır. Kurulu oyun ve v0.1.5 etkilenmez.
- Hyrule Field, Castle Town ve Temple of Time, FG Off
  30 s ısınma + 60 s ölçüm. P50/P95/P99, terminal stall,
  temel FPS, bütçe ve VMA ölçülür. Görsel test geçerse FG
  Auto, gerçek FSR 4.1.2 dispatch ve 3.1 fallback denenir.
- Önerilen bağımsız etiketler `recomp/v0.1.0-rc.1` ve
  `recomp/v0.1.0`. Bunlar mevcut OOT yayın etiketi
  deseninden ayrı. Gelecekte ayrı changelog, kaynak SHA,
  aktarım kaydı, test raporu ve dağıtım manifesti gerekir.
- Ön yayın önce staging'de. Kararlı sürüm ancak kabul
  testleri geçince. Paket, kaynak ve yerel import araçları
  üzerinden dağıtılır. İlk dal hazırlığında yeni build,
  runtime testi veya Release yapılmaz.
