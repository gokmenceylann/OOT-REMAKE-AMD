# Mako 4.1.1 — 1080p replay ve bellek ayrımı

Çalışma dalı performance/stable-mako-411. Başlangıç **4f05ca58d4dac00c66cef5829aa3c6d00fb8b2d3**. GitHub dalı başlangıçla eşleşti ve çalışma ağacı temizdi. Mako kaynağı b77ac861, mako-4.1.1-longshot dalı fa31670. 969be74 ana cache'e uygulanan Windows commit kontrolünü play-cache parçalarına da uyguluyor. 8abb2af quick-pipeline fixture'ını sabitlenen kaynağa uyarlıyor. 4f05ca5 işlem ve sistem commit örneklemesini ekliyor. Main bu çalışmaya alınmadı.

## Bellek ve tahsis sahipleri

WPR CPU + VirtualAllocation, sistem profil politikası nedeniyle 0xc5585011 döndürdü. VirtualAllocation tek başına 0x80070005 ile reddedildi. Allocation/free çağrı yığınları ve heap sahipliği bu koşuda alınamadı.

scripts/Sample-WindowsCommit.ps1 adlı örnekleyiciye -IncludeMakoAddressSpace eklendi. scripts/MakoAddressSpace.cs yalnızca işlem sorgu erişimiyle VirtualQueryEx çalıştırıyor. Bir örnekte PerfProc/PerfOS sayaçları ve Mako 4.1.1 adres bölgeleri UTC ile hizalanıyor. Ayrı sorgular küçük bir zaman aralığında alınır. Commit, Working Set, VMA ve WDDM farklı kapsamları ölçer. Adres bölgesi türleri özel tahsis sahibini veya resident bellek miktarını göstermez.

1080p Native AA koşusunda ilk ölçülen işlem commit'i 7,70 GiB, menü 10,84 GiB, kayıt yükleme başı 10,75 GiB, ilk Castle Town 16,17 GiB, Hyrule Field 20,31 GiB ve Castle Town'a dönüş 22,15 GiB idi. Tepe 23,05 GiB ve sistem commit sınırına kalan en küçük boşluk **0,31 GiB**. Geri dönüşten sonraki bir dakikada adres taraması misafir pencere içinde **9,87–9,89 GiB** committed bölge ve dışarıda **11,70–12,71 GiB** committed private bölge gördü. Bunlar süreç sayacına eklenecek kalemler değildir. HOS misafir aralığının kaynağı third_party/a64-kit/rt/a64.h ve host/hos.h. Misafir heap ve map işlemleri host/hos_mem.c ve host/mkw_glue.c üzerinden Windows commit'i kullanıyor. Misafir aralığının dışındaki artışın GPU driver, shader programları ve diğer host heap sahipleri arasındaki dağılımı doğrulanamadı.

Vulkan heap çıktısı ayrı değerlendirildi. Native AA penceresinde logdaki device-local kullanım 7.839–8.419 MiB ve bütçe 8.722–8.752 MiB. VMA blokları 6.313–7.021 MiB, aktif tahsisler 5.105–6.332 MiB. Cache disk boyutu, driver cache backing, shader nesneleri ve D3D/WDDM süreç sayaçları birbirinin yerine kullanılmadı. Bellek azaltma ve kaynak tahliye kodu değiştirilmedi.

## CPU ölçümünün kapsamı

Native AA oturumunda dönüş sonrası ilk dakika **49,35 ms** replay, **14,20 ms** draw ve **4,98 ms** komut kaydı ölçüldü. Bellek senkronizasyonu **12,40 ms**, bunun içindeki geç GPU sayfa bekleme sayacı **11,17 ms**. Bunlar iç içe zamanlardır. Pipeline beklemesi **0,003 ms** idi. Aynı pencerenin periyodik GPU timestamp ortalaması **28,85 ms**.

RX_VK_PROF_FINE, 120 karelik yayınlarda draw içini kayıtlı kaynak türlerine göre ayırıyor. Yaklaşık hizalanmış Native AA örneklerinde textures **2,90 ms** ortalama, en yüksek 120 kare ortalaması **7,45 ms**, indexed vertex/bind bölümü **1,00 ms**, user uniform **0,98 ms**, descriptor bind **0,95 ms**, storage **0,74 ms** ve pipeline bind **0,22 ms**. Draw çağrısı **1,43 ms**. Bu değerler işlev çağrısı P95'i değildir. vk_draw.cpp texture aşaması handle çözümleme, image view ve sampler, upload hazırlama ve hazard takibi içeriyor. Bu alt işlemleri ayırmadan texture cache, state takibi veya draw sıralamasına müdahale edilmedi.

Her iki koşuda aynı Release Vulkan DLL ve oyun EXE'si, aynı staging kayıtları, FG kapalı, V-Sync açık ve FPS limiti kapalı kullanıldı. Applet çıkışı 1920×1080 idi. Önceki 1536×864 Native AA raporunda handheld_profile etkindi. Güncel koşulda staging ayarlarında kapatıldı. Profiler iki koşuda da açık. Fine profiling için iş kareleri üzerindeki maliyet ayrı bir profiler-kapalı koşuyla ölçülmedi. Dış adres sorgusunun süre sayacı bu profiler maliyetini ölçmez.

## Gerçek oyun koşuları

| Castle Town'a dönüş, ilk 60 saniye | Native AA 1920×1080 | FSR 4.1.2 1440×810 → 1920×1080 |
| --- | ---: | ---: |
| Oyun kare sayacı, yaklaşık 62 saniyede | 22,91/s | 26,45/s |
| Ortalama ham sunum | 20,26/s | 26,30/s |
| 1% low ham sunum | 3,16/s | 11,19/s |
| P50 / P95 / P99 | 32,89 / 105,89 / 167,36 ms | 36,55 / 47,43 / 66,98 ms |
| En uzun sunum aralığı | 635,01 ms | 111,00 ms |
| CPU replay / draw / komut kaydı | 49,35 / 14,20 / 4,98 ms | 38,03 / 14,98 / 6,25 ms |
| Bellek senkronizasyonu / geç sayfa beklemesi | 12,40 / 11,17 ms | 6,25 / 5,12 ms |
| GPU timestamp ortalaması | 28,85 ms (11 örnek) | 22,06 ms (13 örnek) |
| En yüksek süreç private commit (oturum) | 23,05 GiB | 23,50 GiB |
| Sistem commit sınırına en küçük boşluk (oturum) | 0,31 GiB | 0,38 GiB |

Rotalar aynı bölge sırasını izledi. İkinci koşunun ilk teleport isteği oyun etkinliği nedeniyle reddedildi ve tekrarlandı. Kameranın, önceki Castle Town beklemesinin ve etkin cache durumunun eşleşmediği loglarda ve ekran örneklerinde görüldü. Bu nedenle tablo, kontrollü ayar veya kod A/B kazancı olarak kullanılmaz. GPU timestamp'lerinin düşmesi daha az piksel maliyetiyle uyumlu. Aynı koşuda CPU bellek beklemesi de düştü. Göreli katkılar bu testle izole edilemedi. Kare sayacı 30 FPS hedefinin altında kaldı.

%75 koşusunda dokular 120 karelik aralık ortalamalarında **2,54 ms**, descriptor bind **1,12 ms**, indexed vertex/bind **1,16 ms** idi. Vulkan heap kullanımı 7.608–8.400 MiB, bütçe 8.704–8.730 MiB. İki koşuda da save açıldı, FSR 4.1.2 dispatch doğrulandı, rota Castle Town–Hyrule Field–Castle Town tamamlandı ve çıkış kodu sıfırdı. Windows 1455 tekrarlanmadı. İki ekran örneğinde beyaz/yeşil kaplama görülmedi. Native AA geçişinde hazır olmayan draw kaydedildi. Bu koşular tüm geçiş görüntüsünü, 3/5 dakikalık bölge tekrarlarını veya 15 dakikalık kabul testini karşılamaz.

## Değişiklik ve test

85bf1aa yalnız ölçüm aracını değiştirir. Normal süreç örneklemesi, canlı staging runtime adres sorgusu ve Mako rezervasyonu olmayan sürecin reddedilmesi doğrulandı. %75 koşusunda Castle Town penceresinde dış adres taraması medyan 287 ms, azami 372 ms sürdü; bu başka süreçte yapılan periyodik taramanın duvar süresidir. Pipeline commit bütçesi, quick pipelines ve worker yarış/öncelik testleri geçti. Önceki Windows x64 Release renderer kullanıldı. Renderer kaynakları değişmediği için yeni bir performans derlemesi üretilmedi.

Tekrar ölçüm için 64-bit PowerShell'de scripts/Sample-WindowsCommit.ps1 komutuna -GameProcessId, -CsvPath ve -IncludeMakoAddressSpace verilir. WPR çağrı yığınları hem tahsis hem free olaylarıyla alınabildiğinde host private alanı tahsis sahiplerine ayrılabilir. Sonra texture hazırlığında image view lookup, sampler ve kaynak hazırlığı aynı kayıt ve sabit kamera altında ayrı ölçülmelidir. Mevcut yerel v0.1.6 kurulumuna dokunulmadı. Baseline etiketi oluşturulmadı.
