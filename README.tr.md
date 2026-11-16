# OOT-REMAKE-AMD

Hookshot tabanlı Mako 4.1.1 üzerine kurulu Windows 11 x64 Ocarina of Time recomp projesi. AArch64 statik yeniden derleme, Horizon servisleri ve NVN2 → Vulkan çizimi kullanır. Oyun doğrudan `hookshot.exe` ile açılır.

[Kararlı v0.1.6](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/tag/v0.1.6) · [Tanılama ön yayını](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/tag/v0.2.0-rc.4) · [İndirmeler](docs/DOWNLOADS.md) · [English](README.md)

## Hangi sürüm?

| Sürüm | Kullanım |
| --- | --- |
| **v0.1.6, kararlı sürüm** | Doğrulanmış yerel Mako 4.1.1 kurulumunu yeniden derlenen Vulkan DLL ile içe aktarma. GitHub Latest sürümü. |
| **v0.2.0-rc.4, tanılama ön yayını** | Eşleşen yerel test derlemesi için içe aktarıcı ve doku replay ölçümleri. |

Windows x64 kurulum dosyası ve portable ZIP, **yerel oyun içe aktarma araçlarıdır**. Eşleşen `hookshot.exe`, `hookshot_vk.dll`, `image.bin` ve `romfs` kendi yerel derlemenden sağlanır. Kararlı içe aktarma aracı EXE ve DLL’in tam SHA-256 değerlerini kontrol eder. Farklı bir kaynak derlemesi için genel derleme rehberini kullan. Oyun ikilileri, Nintendo içeriği, anahtarlar, oyun türevi önbellekler ve AMD SDK DLL’leri dağıtılmaz.

## Kurulum ve geri dönüş

1. Windows 11 x64 ve Vulkan destekli bir ekran kartı sürücüsü kullan.
2. Kaynaktan derlemek için kendi ExeFS/RomFS verini ve sabitlenmiş araç zincirini hazırla.
3. Kararlı içe aktarmada kaynak oyun klasörünü ve ayrı hedef dizini seç. Ardından hedefteki `hookshot.exe` dosyasını aç.
4. Güncellemeden önce `user/save/` ve `hookshot_options.ini` dosyalarını yedekle. Uyumlu shader ve pipeline cache’i koru.

[Kurulum](docs/install.md#türkçe) · [Kaynak derleme](docs/mako-build.md) · [SHA-256 doğrulama](docs/release.md) · [Sorun giderme](docs/troubleshooting.md)

## RX 6700M test durumu

RX 6700M, Ryzen 7 5800H ve 32 GB RAM ile Vulkan üzerinde test edildi. Kararlı tabanda FG kapalıyken Castle Town → Hyrule Field → Castle Town rotası tamamlandı ve 1536×864 **FSR 4.1.2 Native AA** dispatch’i doğrulandı. Isınma sonrası 56,2 saniyelik kısmi kayıtta ortalama **16,59 sunum FPS**, **147,79 ms P99** ve ayrı oyun kare sayacında yaklaşık **12,79 FPS** ölçüldü. Takılma ve kararlı 30 FPS hedefi açık. FSR 3.1 fallback ve Frame Generation ayrı yollardır.

[Kararlı taban ölçümü](docs/mako-411-baseline-validation.md) · [FSR kurulumu](docs/fsr-4.1.2.md#türkçe) · [Bellek telemetrisi](docs/memory-telemetry.md) · [Bilinen sorunlar](docs/KNOWN_ISSUES.md) · [Takılma incelemesi](docs/stutter-root-cause-report.md)

## Kaynak ve lisans

Kararlı OOT tabanı `93e7586`, sabit Mako kaynağı `b77ac861`. Araştırma ön yayını, Mako’nun zaten devraldığı Longshot değişikliklerinin kaynak izini içerir. Bu pakete yeni Longshot runtime veya ikilisi eklenmedi. Proje bağımsızdır. Upstream GPL ve üçüncü taraf lisans bildirimleri geçerlidir.

[Kaynak kökeni](docs/recomp-source-provenance.md) · [Değişiklikler](CHANGELOG.md) · [Lisans](LICENSE) · [Üçüncü taraf bildirimleri](THIRD-PARTY.md)
