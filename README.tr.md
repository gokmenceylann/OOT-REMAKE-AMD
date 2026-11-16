# OOT-REMAKE-AMD

Hookshot tabanlı Mako 4.1.1 üzerine kurulu Windows 11 x64 Ocarina of Time recomp projesi. AArch64 statik yeniden derleme, Horizon servisleri ve NVN2 → Vulkan çizimi kullanır. Oyun doğrudan `hookshot.exe` ile açılır.

Yayımlanan raporlar Radeon RX 6700M üzerinde yapılan kısmi doğrulamayı kayda geçiriyor. Castle Town takılmaları, Windows bellek taahhüdü baskısı ve bölge geçişlerindeki eksik çizimler için doğrulanmış bir çözüm henüz yok. Sorunu yeniden üreten testler ve ölçümle doğrulanan düzeltmeler katkıya açık. [Açık bulgular ve katkı takibi](https://github.com/gokmenceylann/OOT-REMAKE-AMD/issues/5)

[Kararlı v0.1.6](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/tag/v0.1.6) · [Deneysel v0.2.0-rc.4](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/tag/v0.2.0-rc.4) · [İndirmeler ve sürüme özel kurulum](docs/DOWNLOADS.md) · [English](README.md)

## Hangi sürüm?

| Sürüm | Kullanım |
| --- | --- |
| **v0.1.6, kararlı sürüm** | Doğrulanmış yerel Mako 4.1.1 kurulumunu yeniden derlenen Vulkan DLL ile içe aktarma. GitHub Latest sürümü. |
| **v0.2.0-rc.4, tanılama ön yayını** | Eşleşen yerel test derlemesi için içe aktarıcı ve doku replay ölçümleri. |

Windows x64 kurulum dosyası ve portable ZIP, **yerel oyun içe aktarma araçlarıdır**. Eşleşen `hookshot.exe`, `hookshot_vk.dll`, `image.bin` ve `romfs` kendi yerel derlemenden sağlanır. Her yayın kurucusu EXE ve DLL’in kendi manifestindeki SHA-256 değerlerini denetler. Farklı bir kaynak derlemesi için genel derleme rehberini kullan. Oyun ikilileri, Nintendo içeriği, anahtarlar, oyun türevi önbellekler ve AMD SDK DLL’leri dağıtılmaz.

## Kurulum ve geri dönüş

1. Windows 11 x64 ve Vulkan destekli bir ekran kartı sürücüsü kullan.
2. Kaynaktan derlemek için kendi ExeFS/RomFS verini ve sabitlenmiş araç zincirini hazırla.
3. Kararlı içe aktarmada kaynak oyun klasörünü ve ayrı hedef dizini seç. Ardından hedefteki `hookshot.exe` dosyasını aç.
4. Güncellemeden önce `user/save/` ve `hookshot_options.ini` dosyalarını yedekle. Uyumlu shader ve pipeline cache’i koru.

[Kurulum](docs/install.md#türkçe) · [Kaynak derleme](docs/BUILDING.md) · [SHA-256 doğrulama](docs/release.md) · [Sorun giderme](docs/troubleshooting.md)

## RX 6700M test durumu

RX 6700M, Ryzen 7 5800H ve 32 GB RAM ile Vulkan başlangıcı, kayıt yükleme ve bölge geçişleri test edildi. Deneysel rc.4 koşularında FG kapalıyken gerçek FSR 4.1.2 Vulkan dispatch’i kaydedildi. Castle Town takılması, geçişlerde hazır olmayan çizimler ve bellek baskısı açık. Diğer AMD GPU’lar ile NVIDIA ve Intel GPU’lar için yayımlanmış doğrulama yok. [GPU uyumluluğu ve test koşulları](docs/GPU_COMPATIBILITY.md)

[Kararlı taban ölçümü](docs/mako-411-baseline-validation.md) · [FSR kurulumu](docs/fsr-4.1.2.md#türkçe) · [Bellek telemetrisi](docs/memory-telemetry.md) · [Bilinen sorunlar](docs/KNOWN_ISSUES.md) · [Takılma incelemesi](docs/stutter-root-cause-report.md)

## Kaynak ve lisans

Kararlı v0.1.6 commit’i 66aa0e1, sabit Mako 4.1.1 kaynağı b77ac861. Longshot kaynak izleme ve karşılaştırma kayıtlarında yer alıyor. Upstream GPL ve üçüncü taraf lisans bildirimleri geçerlidir.

[Kaynak kökeni](docs/UPSTREAM-PROVENANCE.md) · [Değişiklikler](CHANGELOG.md) · [Lisans](LICENSE) · [Üçüncü taraf bildirimleri](THIRD-PARTY.md)
