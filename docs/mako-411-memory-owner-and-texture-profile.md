# Mako 4.1.1 — bellek sınıfları ve texture replay profili

## Kaynak ve test tabanı

Başlangıç ve doğrulanan uzak HEAD e13267cb76ade92b644bbdd978ae8de0edeb34ef, dal performance/stable-mako-411. Çalışma ağacı temizdi. Mako gitlink b77ac861. e13267c önceki 1080p izini, 85bf1aa guest/host adres sınıflandırmasını, 969be74 play-cache commit korumasını, 8abb2af quick-pipeline fixture'ını ve 4f05ca5 süreç commit örnekleyicisini içeriyor. Main ve Longshot aktarımı yok.

99b18af, vk_draw.cpp içindeki image view, kaynak hazırlığı, sampler ve hazard ölçümünü patch olarak ekliyor. Build-LocalGame.ps1 ve Windows renderer CI patch'i uyguluyor. Test production scope'u sahte saatle derleyip kapalı/açık durum, 16'da bir örnekleme, iç içe zamanlama, thread izolasyonu ve sayaç sıfırlamayı doğruluyor. Araç RX_VK_TEXTURE_PROFILE=1 ile çalışır, varsayılan kapalıdır. Yalnızca raporlayan replay thread'inin scope'larını sayar. 120 karelik loglar tahmini ortalama ve çağrı sayısı verir. Texture preparation view içinde ölçülür. Bu süreleri toplamak çift sayım olur.

## Windows tahsis sınıfları

WPR'da Heap, HeapSnapshot, CPU ve VirtualAllocation profilleri mevcut. Önceki CPU + VirtualAllocation 0xc5585011, VirtualAllocation tek başına 0x80070005. Bu oturumda Heap.Light.File ve HeapSnapshot.Verbose.File de 0x80070005 verdi. Microsoft-Windows-Kernel-Memory ve Microsoft-Windows-Heap-Snapshot sağlayıcıları keşfedilebildi. Sağlayıcı listesi stack-enabled trace vermez.

Microsoft imzası doğrulanan VMMap x64 ile yalnızca staging PID'sine ait CSV snapshot alındı. Araç heap, anonim private data, file mapping, executable image ve stack türlerini ayrı raporladı. PerfProc/PerfOS ve VirtualQueryEx sayımları ayrıca 10 saniyede bir alındı. Bunlar farklı zamanlarda tamamlanabilen, birbirine eklenmeyecek sayaçlardır. Ham snapshot ve araç diskteki test dizininde kaldı. [Microsoft VMMap](https://learn.microsoft.com/en-us/sysinternals/downloads/vmmap)

| VMMap snapshot | Toplam private | Heap private | Anonim private data | Stack private |
| --- | ---: | ---: | ---: | ---: |
| Açılış örneği, intro | 10,79 GiB | 2,29 GiB | 8,32 GiB | ~5 MiB |
| Menü | 10,83 GiB | 2,29 GiB | 8,37 GiB | ~5 MiB |
| Save açıldı | 17,86 GiB | 2,52 GiB | 15,16 GiB | ~5 MiB |
| Hyrule Field ilk giriş | 20,13 GiB | 2,70 GiB | 17,25 GiB | ~5 MiB |
| Hyrule Field ikinci giriş | 23,00 GiB | 3,48 GiB | 19,35 GiB | ~5 MiB |
| Castle Town ikinci giriş | 23,14 GiB | 3,48 GiB | 19,48 GiB | ~5 MiB |

İlk Castle Town snapshot'ı ayrıntı ve toplam satırları uzlaşmadığı için tablodan çıkarıldı. Menü ve ikinci Castle Town ayrıntılarını adres aralığına göre böldüğümüzde anonim private data'nın guest payı **5,57 → 9,97 GiB**, guest dışı payı **2,80 → 9,52 GiB**. Heap sınıfı aynı pencerede **2,29 → 3,48 GiB**. Stack artışı bu ölçümlerde GiB ölçeğinde bir açıklama sunmuyor. Save örneğinde Vulkan pipeline cache dosyası yaklaşık 1,45 GiB'lik eşlemede göründü. Bu eşlemenin Private sütunu boştu. Dosya eşlemesini anonymous private olarak saymadık.

Guest adres alanının sahibi HOS. Guest dışındaki anonim blokların AMD sürücüsü, shader/FSR, renderer buffer/cache veya başka bir host ayrıştırması yok. Heap ve stack sınıflandırması tahsis çağrı yığınlarını vermez. Allocation/free sayısı, Vulkan ayırıcı callback sahipliği ve bireysel nesne yaşam süresi belirsiz. Vulkan texture retirement logları kaynak bırakıldığını gösteriyor fakat Windows private commit değişimini her bir kaynağa bağlamıyor.

## Profiler maliyeti

Production scope'u çıkaran x64 C++ mikrotestinde, steady_clock kullanılan yalıtılmış çağrı için üç tekrar medyanı kapalı **3,17 ns**, açık **7,00 ns**. Bu yalnızca scope mekanizmasıdır. Oyunun gerçek saat kaynağını, periyodik loglamayı, VMMap taramasını ve eş koşullu profiler açık/kapalı oyun FPS'ini ölçmez.

## Native AA donanım ölçümü

FG kapalı, 1920×1080 Native AA, Vulkan RX 6700M, mevcut oyun EXE'si ve yeni Windows x64 Release renderer DLL'i. Log, FSR 4.1.2'yi 1920×1080 → 1920×1080 olarak kaydetti. Açılış → menü → save Castle Town → Hyrule Field → Castle Town → Hyrule Field → Castle Town tamamlandı. İkinci Castle Town girişinden yaklaşık 4 dakika 38 saniye sonra pencere kapandı. Son kontrol örneği 4 dakika 26 saniyede hâlâ Castle Town'daydı. Tüm oturum 434 saniye, çıkış 0; 1455 ve uygulama çökmesi kaydedilmedi. Beş dakikalık bölge beklemesi ve 15 dakikalık kabul oturumu tamamlanmadı.

İkinci Castle Town girişinden sonraki ilk 60 saniyede CPU replay **57,68 ms**, CPU draw **14,04 ms**, komut kaydı **5,32 ms**, bellek senkronizasyonu **17,74 ms**, bunun içindeki geç GPU sayfa beklemesi **16,22 ms**. Pipeline beklemesi izde 0,00 ms. Kare başına mevcut işlerin alt dilimleri birbirine eklenmez. Dokuz periyodik GPU timestamp özeti **35,48 ms** ortalama, **17,7–76,6 ms** aralığı verdi. Windows WDDM 3D motoru altı örnekte **%63–92**. Draw özetleri **1.217–2.661 draw/kare**.

| Texture scope | Yaklaşık ms/kare | Çağrı / zaman örneği |
| --- | ---: | ---: |
| texture_view_of, iç hazırlık dahil | 2,478 | 10.314.896 / 644.685 |
| View içindeki texture_get veya touch hazırlığı | 1,702 | 1.170.762 / 73.176 |
| sampler_for | 0,221 | 11.598.318 / 724.899 |
| Hazard ve render pass hazırlığı | 0,171 | 4.394.880 / 274.685 |

Sayaçlar dokuz 120-kare raporundan. Rapor penceresi sunum CSV sınırlarıyla yaklaşık hizalı. View süresi texture hazırlığını içerir. texture_get ve touch maliyeti kaynak doğrulama, image lookup/oluşturma ve upload hazırlığına giden yolları birlikte içerir. Saf upload hazırlığı veya kilit süresi bağımsız sayılmadı. Alt işlev P95, ETW stack ve allocation/free sayısı elde edilmedi. Ölçüm, sampler lookup'ı bu koşudaki ana CPU adayı olarak göstermiyor. Daha büyük gecikme guest GPU write-back beklemesi. Bu beklemenin güvenle kaldırılabileceği kanıtlanmadı. Replay, tahliye, draw sırası veya FSR davranışını değiştiren optimizasyon uygulanmadı.

Native AA süreç private commit tepesi **23,22 GiB**, ROM/renderer test sürecine ait Working Set o anda **15,24 GiB**. Sistem commit boşluğu en az **0,32 GiB**. İkinci Castle Town beklemesinin son örneği **22,39 GiB** süreç commit'i, **10,0 GiB** guest committed bölge, **12,16 GiB** guest dışı private bölgeydi. Private commit tepe sonrası geriledi. Aynı rota daha fazla tekrar edilmeden bunu sızıntının yokluğu olarak kullanamayız. Vulkan device-local kullanım ilk dakikada **7.907–8.697 MiB**, bütçe **8.697–8.725 MiB**, VMA **119–125 blok/6.365–7.205 MiB**, **1.765–1.879 aktif tahsis/5.080–5.466 MiB**. Vulkan fiziksel VRAM kapasitesi yerine heap bütçesini raporluyor.

## Derleme ve regresyon

Windows x64 Release Vulkan DLL'i bağlandı. Mevcut oyun EXE'si staging ile kullanıldı. Texture scope fixture'ı, pipeline commit bütçe testi, quick-pipeline vakaları, worker yarış/öncelik ve hata kurtarma, device-loss yönlendirme fixture'ı geçti. Vulkan validation layer ile canlı oyun koşusu yapılmadı. Native AA'da hazır olmayan draw olayları tamamen sıfırlanmadı. Staging ekran görüntüsü tek karelik görsel örnektir.

## %75 FSR koşusu ve kabul durumu

Ayrı yeniden başlatmada FSR 4.1.2 **1440×810 → 1920×1080** dispatch'i doğrulandı. Save açıldı ve Hyrule Field → Castle Town tamamlandı. Pencere 83,42 saniyede normal çıkışla kapandı. İkinci Castle Town geçişi ve eş 60 saniyelik pencere tamamlanmadı. İlk Castle Town girişinden 10 saniyelik ham sunum örneği 16,63/s, 1% low 2,85/s, P50 48,71 ms, P95 132,46 ms, P99 299,78 ms ve maksimum 400,93 ms verdi. Native AA'nın ikinci girişinden 60 saniyelik örnek 17,34/s ham sunum, yaklaşık 16,41/s oyun sayacı, 1% low 6,05/s, P50 47,66 ms, P95 99,32 ms, P99 130,30 ms ve maksimum 355,68 ms. Pencereler ve sahne geçmişi farklı. Doğrudan FPS kazancı hesaplanmadı. Üç tekrarlı A/B tamamlanmadı. %75 koşusunun örneklenen private commit tepesi 21,88 GiB. 1455 veya guest exception kaydı yok.

Native AA ekran örneğinde beyaz/yeşil kaplama görülmedi. Tam geçiş boyunca görsel regresyon kontrolü tamamlanmadı. Tahsis sahipliği ve 30 FPS kabul kriteri açık. Yerel v0.1.6 EXE ve DLL hash'leri başlangıçla eşleşti. Yeni baseline etiketi oluşturulmadı.
