# Castle Town performans incelemesi

## Temel ve test koşulları

- Kararlı temel: `v0.1.6`, `66aa0e1a92777d47cdca9e0d870374b862cd5730`. Mako 4.1.1 kaynağı: `b77ac86187330eb7447ac65ab23187baac4600ca`.
- Windows 11, Ryzen 7 5800H ve Radeon RX 6700M. İki koşuda aynı `hookshot.exe`, başlangıç kaydı ve cache yedeği, FG kapalı, V-Sync açık, FPS limiti kapalı. Renderer her iki koşuda da Castle Town ölçümünden önce FSR 4.1.2 Native AA dispatch'ini 1536×864 → 1536×864 olarak kaydetti. Adayda tek runtime farkı Vulkan DLL'indeki geç sayfa kopyasıydı. Deneysel warmup yamaları uygulanmadı.
- Test rotası Castle Town → Hyrule Field → Castle Town. Özel kontrol köprüsüyle bölge geçişi yapıldı. İlk koşuda ölçümden önce fazladan bir geçiş isteği reddedildi. Kamera ve oyun olayları kare düzeyinde sabitlenemedi. Ortak 20 saniye, Castle Town'a dönüşten sonraki ilk kontrol noktasından başlar. Aday daha sonra Hyrule Castle'a geçti ve görüntü örneği o geçişte yükleme ekranına denk geldi. Bu yüzden eşleşmiş 60 saniyelik A/B ve görsel regresyon doğrulaması yapılamadı.

## Sonuçlar

| Castle Town, ortak ilk 20 saniye | Kararlı | Aday |
| --- | ---: | ---: |
| Ortalama sunulan FPS | 21,17 | 21,43 |
| 1% low FPS | 10,11 | 8,88 |
| P95 sunum aralığı | 73,06 ms | 74,40 ms |
| P99 sunum aralığı | 90,98 ms | 107,71 ms |
| En uzun sunum aralığı / karşılığı | 112,29 ms / 8,91 FPS | 115,93 ms / 8,63 FPS |
| CPU replay, ortalama duvar süresi | 47,25 ms | 46,66 ms |
| CPU replay içinde bellek senkronizasyonu | 10,50 ms | 6,27 ms |
| Geç sayfa için GPU zaman çizelgesi beklemesi | 9,14 ms | 4,63 ms |
| CPU draw aşaması / komut kaydı | 14,74 / 5,99 ms | 18,43 / 6,66 ms |
| Pipeline/shader beklemesi | 0,00 ms | 0,12 ms |
| GPU timestamp özeti (periyodik log) | 32,87 ms (3 örnek) | 21,93 ms (4 örnek) |
| VMA device-local blokları / tahsisleri (anlık) | 6525 / 4724 MiB | 6341 / 5477 MiB |
| Vulkan device-local heap kullanım / bütçe (anlık) | 8030 / 8320 MiB | 7719 / 8324 MiB |
| WDDM ayrılmış / paylaşılan süreç belleği | 7,14 / 3,46 GiB (1 örnek) | 6,96–7,36 / 3,85–4,38 GiB (4 örnek) |

CPU replay süresi beklemeleri de içerir. Alt sayaçlar iç içe geçebilir. Örneğin geç sayfa beklemesi bellek senkronizasyonunun içindedir. GPU timestamp özetleri ve WDDM örnekleri dönüş olayının zamanından yaklaşık hizalandı. Kare başına CPU ölçümüyle toplanmaz ve GPU farkı adayın kazancı olarak yorumlanamaz. WDDM süreç sayaçları, Vulkan heap bütçesi ve VMA blok/tahsis değerleri farklı kapsamları ölçer. Fiziksel VRAM kapasitesi bu sayaçlardan çıkarılmadı. Her iki koşunun VMA telemetrisinde sıfır tahsis hatası kaydedildi.

Kararlının Castle Town'da geçirdiği ayrı 60 saniyelik sıcak pencere: **32,97 FPS**, **12,55 FPS 1% low**, **47,21 ms P95** ve **70,06 ms P99**. Ortalama CPU replay 30,33 ms, ortalama GPU timestamp özeti 15,12 ms (16 örnek). Sunum ve oyun ana iş parçacığı sırasıyla bir çekirdeğin yaklaşık %67 ve %40'ını kullandı. CPU draw aşaması 9,89 ms, komut kaydı 3,76 ms, bellek senkronizasyonu 2,85 ms ve pipeline beklemesi 0,003 ms. Periyodik sunum özetlerinde yaklaşık 1100–2500 draw/kare görüldü. Görünür benzersiz nesne sayacı mevcut değildi.

Kontrol talebinin kabulünden hedef bölgenin bildirimine Castle Town → Hyrule Field geçişi 10,48 / 6,64 saniye, dönüş 6,11 / 6,23 saniye sürdü (kararlı / aday). Bu süreler oyun olaylarını ve yüklemeyi içerir. Aynı yükleme durumunu kare düzeyinde sabitlemeden bir hızlanma çıkarılamaz.

## Kod deneyi ve karar

`gpu/vk/vk_memory.cpp` içindeki `take_capture`, GPU'nun misafir belleğine geri yazmasını `vk_timeline_wait(c->late_value)` ile bekler. CPU sonra ilgili 4 KiB sayfaları eşlenmiş Vulkan arabelleğine kopyalayıp flush eder. Aday, beklemeden sonraki bitişik kaynak ve hedef sayfalarını tek korumalı kopyada birleştirdi. Birleşik çağrı erişim hatası alırsa sayfaları tek tek yeniden denedi. Fence, tahsis, flush ve upscaler davranışına müdahale edilmedi. Ayrı fonksiyon testinde yedi sayfalık örnek üç kopya çağrısına düştü. Boş liste, aralık boşlukları ve erişim hatasından sonra kalan sayfaların işlenmesi de geçti.

Erken bölge penceresinde bellek senkronizasyonu belirgin bir maliyet. Adayın kopyayı gruplaması GPU beklemesini doğrudan değiştirmediğinden, iki koşudaki bekleme farkı tek başına adayın etkisini göstermez. Sıcak sahnede CPU draw hazırlığı, ölçülen CPU alt aşamalarının en büyüklerinden biri. Bir sonraki kontrollü testte `gpu/vk/vk_draw.cpp` içindeki draw hazırlığı ve komut kaydı, aynı kamera girdisi ve aynı draw yüküyle ayrı ölçülmeli. GPU geri yazma bağımlılıkları korunmalı.

Adayın FPS kazancı doğrulanmadı ve 1% low ile P99 olumsuz yönde değişti. Aday kaynak yaması geri alındı. Ölçüm raporu dışında çalışan dalın runtime dosyalarında değişiklik yapılmadı. Yerel oyunun EXE/DLL SHA-256 değerleri başlangıçla eşleşti. Yerel kayıt, ayar ve önbellek staging dışında bırakıldı.

## Derleme ve regresyon testleri

- Oyun A/B'si için kurulu v0.1.6 ile aynı optimizasyon seçenekleriyle Windows x64 renderer DLL'i derlendi ve mevcut oyunun EXE'siyle ayrı staging dizininde çalıştı.
- Aday için ek olarak `RX_RELEASE=1` ve `RX_VK_ONLY=1` ile Windows x64 Release renderer derlemesi geçti. 206 dosya derlendi, sıfır hata bildirildi ve `hookshot_vk.dll` bağlandı. Oyun EXE'si yeniden derlenmedi. Release bayrağıyla üretilen ayrı DLL A/B için kullanılmadı.
- Mako renderer worker hata kurtarma ve Vulkan import regresyonları geçti (37 import vakası). Mevcut capture-copy testi ve adayın ayrı C++ kopyalama testi de geçti.
- Sunum ölçümleri `Capture-VulkanSession.ps1` ve `Measure-FrameTimes.ps1`, WDDM örnekleri `Sample-GpuMemory.ps1`, replay sayaçları `RX_VK_FRAME_TRACE=1` ile alındı. Aday süreç çıkış kodu 0 ve son kapanış kaydı pencerenin kapanmasıydı.
