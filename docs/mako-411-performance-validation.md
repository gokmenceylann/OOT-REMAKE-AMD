# Mako 4.1.1 performans dalı — doğrulama durumu

## Kaynak tabanı

- Dal: `performance/stable-mako-411`. Başlangıç: `fa3167067ebeb0c058e9983c27e51bed66bc711a` (`mako-4.1.1-longshot`).
- Kurulu v0.1.6: `66aa0e1a92777d47cdca9e0d870374b862cd5730`. Upstream Mako 4.1.1: `b77ac86187330eb7447ac65ab23187baac4600ca`. Renderer API 23.
- Runtime yamalarının başlangıç envanteri: `fsr-4.1.2.patch`, `rx6700m-memory.patch`. Worker ve import doğrulaması için `mako-411-regression-fixture.patch` kullanılıyor. Karşılaştırma için incelenen main: `d7782905437d4502865e721546da8b9bdf51fa67`. Main'deki warmup yamaları ve yeni Longshot kaynakları bu dala alınmadı.

## Değişiklikler

| Commit | Değişiklik ve kapsam |
| --- | --- |
| `771b92fc5216e1eaa0b95f571478ac12ac3c633e` | `patches/mako-411-pipeline-queue.patch`: `gpu/vk/vk_jobs.cpp` iş sırasını mevcut deque elemanlarını döndürerek değiştiriyor. İş, tamamlanma işaretçisi ve hata callback'i kuyrukta kalıyor. Ek tahsis olmadan öncelik yükseltme testi ekli. |
| `db4c0145f150049186113af621c5a9a29ac6853d` | `patches/mako-411-on-demand-startup.patch`: `gpu/vk/vk_draw.cpp` Release'te olağan açılışın kararlı sürümdeki isteğe bağlı pipeline hazırlığını kullanmasını sağlıyor. `RX_VK_PRECOMPILE=1` ve bağımsız `--prepare-shaders` yolu korunuyor. `tests/test_mako_startup_policy.py` Release politikasını derleyerek test ediyor. |
| Her iki commit | `scripts/Build-LocalGame.ps1` ve `.github/workflows/renderer.yml` patch sırasını ve testleri bağlıyor. |

Yüksek öncelikli iş için eski kod önce kuyruktaki elemanı kaldırıyor, sonra başa ekliyordu. Deney, kuyruğun dolu bölümünde tekrar öncelik yükseltmenin eski sürümde tahsis yaptığını ve yenisinde yapmadığını ölçtü. Tahsis başarısız olursa kaldırılmış işin callback'i de kaybolabiliyordu. Bunun geçmiş oturumlarda gerçekleştiği veya beyaz/yeşil görüntüyü tetiklediği doğrulanmadı.

İlk Release oyun koşusunda normal başlangıç, 20.774 program ve 26.235 grafik pipeline notunu açtı. Süreç private commit'i hazırlık öncesindeki 1.490 MiB'den hazırlık sonrasında 12.791 MiB'ye çıktı. Kayıt açıldı ve Hyrule Field'a geçildi. Sonra Windows, misafir RAM'i için yaklaşık 31 MiB tahsiste **1455** döndürdü. Crash stack'i `memory_sync` üzerinden C++ exception gösterdi. Bu bir Windows sistem commit hatasıydı. Önceki VMA telemetrisinde tahsis hatası sıfırdı. Aynı DLL'in `RX_VK_PRECOMPILE=0` ile çalıştırılması kayıt yükleme ve gidiş-dönüş rotasını tamamladı. Çalışma dizini, cache ve sistem yükü koşular arasında değişebileceğinden bu gözlem kesin bir bellek sınırı tanımlamaz.

## Pipeline ve görüntü doğruluğu

`graphics_pipeline` tam anahtara göre renderer tablosunda bir giriş kullanıyor. `draw` içinde hazır olmayan giriş, pipeline ve hedef türüne göre iş bekletebiliyor veya çizimi atlayabiliyor. Daha önceki 39 yavaş derleme ve 45.647 ms toplam derleme ölçümü main'deki başka bir koşuya ait. Güncel çalışmada geçiş çevresinde `draws left out (not ready)` tekrar görüldü. Bu, gerekli çizimlerin tamamlanmasını garanti eden yeni bir mekanizmanın hâlâ eksik olduğunu gösterir. Tek başına hangi yüzeyin neden beyaza veya yeşile döndüğünü belirlemez.

Bir sonraki adımda, geçiş sırasında boş kalan çizimleri kaynak tüketimi ve tam pipeline anahtarıyla eşleştirmek gerekiyor. Renderer ilk gerekli çiziminden önce pipeline isteğini üretmeli. Dış kaynak yazan veya yeni hedefe çizen komutlar için sıra ve kaynak ömrü korunmalı. Derleyici bitene kadar mevcut yaklaşımın hangi çerçeveyi gösterdiği de render sırası değişmeden doğrulanmalı. Bu aşamada bölge profili, yeni komut erteleme kuyruğu, descriptor/draw optimizasyonu ve bellek senkronizasyonu optimizasyonu uygulanmadı.

## Otomatik testler

- Windows x64 Vulkan Release DLL her iki adımda da derlenip bağlandı. Oyun EXE'si yeniden derlenmedi.
- Worker öncelik ve yarış testleri, worker/serial/steal hata kurtarma, Vulkan import (37 vaka), pipeline cache başlığı, stamp ve fetch kilidi, Vulkan sunum device-loss yolları ve temporal history (7.647 kontrol) geçti.
- Yeni kuyruk testi ve Release başlangıç politikası testi eski kodda beklenen kontrol noktasında başarısız oldu, yamalı kodda geçti.
- `test_quick_pipelines.py` mevcut kaynakta ilk metin varsayımında başarısız. Test, `st_pipelines++` için belirli bir blok ve yorum bekliyor. Sabitlenen Mako commit'i sayacı aynı `!quick_build` koşulu altında farklı biçimde yazıyor. Bu test tam geçiş olarak sayılamaz.
- Gerçek Vulkan device loss enjeksiyonu, kuyruk kapatma/iptal matrisi ve gerçek bozuk cache oyun testi bu koşuda yapılmadı.

## RX 6700M oyun doğrulaması

Son Release DLL, ayrı staging dizininde `RX_VK_PRECOMPILE` ayarlanmadan mevcut x64 EXE ile açıldı. Save açıldı, Castle Town → Hyrule Field → Castle Town rotası tamamlandı, FSR 4.1.2 Native AA 1536×864 → 1536×864 dispatch'i kaydedildi. Frame Generation kapalı, V-Sync açık, FPS limiti kapalıydı. Toplu açılış ön derlemesi logda görülmedi. Aynı Windows 1455 hatası tekrarlanmadı ve süreç çıkış kodu 0 oldu. Bölgeye dönüşten sonraki ekran örneklerinde beyaz/yeşil kaplama görülmedi. Geçişe yakın logda kare başına ortalama 7,4 hazır olmayan çizim bildirildiği için tüm geçişin görsel olarak doğru olduğu doğrulanamadı.

Dönüşten sonraki ilk 60 saniyenin sunum telemetrisi 2.886 aralık ölçtü. Ortalama ham sunum sayısı **48,07/s**, 1% low **4,75/s**, P50 **13,08 ms**, P95 **45,94 ms**, P99 **64,86 ms** ve maksimum **3.710,29 ms**. Kontrol köprüsü de aynı bölümde bir takılma bildirdi. Köprünün ayrı oyun kare sayacı ilk 62,44 saniyede 1.702 ilerledi (~**27,3/s**). Sunum ve oyun sayaçlarının ayrışması nedeniyle 48,07 gerçek render FPS olarak kullanılmadı. Bu koşunun kamera, cache ve sistem durumu önceki kararlı 60 saniyelik koşuyla eşleşmiyor. FPS farkı hesaplanmadı.

Kare izi özeti CPU replay **35,52 ms**, draw **12,91 ms**, komut kaydı **5,00 ms**, bellek senkronizasyonu **2,84 ms**, pipeline hazırlık CPU aşaması **0,54 ms**, pipeline beklemesi **0,001 ms**. Periyodik GPU timestamp özeti **16,73 ms** (14 örnek). Bu ortalamalar 3,7 saniyelik kesintiyi açıklamaz. Yakın zaman aralığında 995, 497 ve 524 ms süren arka plan derleme kayıtları var. Bunların kesintinin nedeni olduğu gösterilemedi.

Device-local heap kullanımı **7.844–7.908 MiB**, Vulkan budget **8.986–9.001 MiB**. İlgili VMA blokları **6.337–6.401 MiB**, tahsisleri **4.921–5.546 MiB**. VMA tahsis hatası sıfır. WDDM ayrılmış süreç belleği **6,96–7,99 GiB**, paylaşılan **2,09–4,48 GiB** (12 örnek). Sayaçlar farklı kapsamları ölçer ve fiziksel kapasite değerini vermez.

Hyrule Field geçişi smoke test olarak yapıldı. Bağımsız 60 saniyelik Field penceresi, tam video üzerinden ilk kare doğrulaması, otomatik aynı kamera A/B ve 15 dakikalık oturum tamamlanmadı. Oyunu yeniden açıp aynı kaydı yükleme farklı aday derlemelerle denendi. Son DLL için aynı ikiliyle ayrı bir yeniden başlatma matrisi çalıştırılmadı.

## Karar ve geri dönüş

Bu dal doğrulama dalıdır. Kurulu `hookshot.exe`, `hookshot_vk.dll`, kayıtlar ve cache test dizini dışından değiştirilmedi. İlgili oyun kayıtları, ekran görüntüleri, SDK DLL'leri veya cache GitHub'a eklenmedi. Yeni baseline etiketi için eksik çizimin giderilmesi, eş koşullu performans kazancı ve en az 15 dakikalık kararlılık doğrulaması gerekiyor. Geri dönüş referansı `fa3167067ebeb0c058e9983c27e51bed66bc711a`; kurulum referansı `v0.1.6`.
