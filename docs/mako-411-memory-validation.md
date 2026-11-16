# Mako 4.1.1 bellek ve geçiş doğrulaması

Başlangıç **2524779aceea5c913b6f0530e76886d84d7a0bd5**, GitHub dalı performance/stable-mako-411. Mako gitlink'i **b77ac86187330eb7447ac65ab23187baac4600ca**. Başlangıç çalışma ağacı temizdi. 771b92f iş önceliğini tahsissiz değiştiriyor, db4c014 Release açılışında toplu ön derlemeyi isteğe bağlı yapıyor. Main ve Longshot değişiklikleri aktarılmadı.

## Kaynak incelemesi ve düzeltmeler

- Eski Release logunda toplu hazırlığın private commit ölçümleri **1.490 → 3.038 → 7.625 → 12.791 MiB**. Ara ölçümler sırasıyla Vulkan cache açıldıktan, 26.235 pipeline notu ve 20.774 program okunduktan ve hazırlık tamamlandıktan sonra alındı. Daha sonraki misafir RAM commit isteği **0x1f00000 bayt (31 MiB)**, Windows **1455** ile başarısız oldu. Bu ölçümler bütün bellek baskısını tek başına ön derlemeye bağlamak için yeterli değil.
- **969be74**, gpu/vk/vk_draw.cpp içindeki play_files_merge yoluna ana cache için kullanılan Windows commit sınırını ekler. Her oyun cache parçası için bütçe driver'a verilmeden önce yeniden okunur. Reddedilen veya Vulkan import/merge hatası veren dosya korunur. Geçici VkPipelineCache merge çağrısından sonra yok edilir. Salt okunur dosya eşlemesi, oluşturma çağrısı döndükten sonra bırakılır.
- Normal oyunda dört parça, toplam **18.070 KiB**, birleştirildi. Aynı koşuda bütçenin bir parçayı reddettiği görülmedi. Sınırda reddetme ve ölçüm yokluğu sentetik regresyonda doğrulandı. Bu düzeltme için oyun içi RAM düşüşü ölçülmedi.
- **8abb2af**, sabitlenmiş Mako'nun sayaç ve fixture biçimine eski quick-pipeline testini uyarlar. Renderer davranışını değiştirmez. AMD/NVIDIA için yedi fixture koşulu geçti. Worker öncelik/yarış ve hata kurtarma, pipeline bütçe eşikleri, dosya başlığı ve stamp, sunum device-loss yönlendirmesi ve 7.647 temporal history kontrolü geçti. Windows x64 Release renderer DLL bağlandı. Oyun EXE'si yeniden derlenmedi.
- Kaynak incelemesinde recording_wait sonrası command pool ve slot descriptor pool geri kullanımı, vk_texture.cpp'de ertelenmiş image imhası ve FSR context emekliliği tespit edildi. Tam Vulkan lifecycle ve shutdown doğrulaması yapılmadı. PlayCache kontrol nesnesinin proses ömrünce tutulduğu upstream yorumunda açıkça belirtiliyor. Bu küçük yapı, ölçülen GiB ölçeğindeki süreç commit artışının açıklaması olarak gösterilemez.

## Windows süreç ve sistem commit ölçümü

Ölçümler scripts/Sample-WindowsCommit.ps1 ile aynı UTC zaman sütununda alındı. Aşama sınırlarına en yakın örnek seçildi. Windows PerfProc PageFileBytes burada süreç commit sayacı olarak ayrı tutuldu ve bu testte PrivateBytes ile aynı değeri verdi. İki değer toplanmaz. Working Set fiziksel bellekteki sayfaları gösterir. Vulkan ve WDDM ayrı kaynaklara aittir.

| Aşama | Private / süreç commit (GiB) | Working Set (GiB) | Sistem commit / limit (GiB) |
| --- | ---: | ---: | ---: |
| Açılışta ilk örnek | 4,17 / 4,17 | 3,52 | 21,05 / 37,39 |
| Menü | 8,70 / 8,70 | 6,13 | 25,67 / 37,39 |
| Kayıt yükleme başlangıcı | 9,05 / 9,05 | 6,48 | 26,01 / 37,39 |
| İlk oynanabilir Castle Town | 14,42 / 14,42 | 8,31 | 31,41 / 37,39 |
| Hyrule Field | 19,09 / 19,09 | 11,54 | 36,24 / 37,39 |
| Castle Town'a dönüş | 20,72 / 20,72 | 13,38 | 37,82 / 38,40 |

Sistem commit limiti koşu sırasında büyüdü. Örneklenen boşluk yaklaşık **0,40 GiB** seviyesine kadar indi. Oyun başlangıçta Castle Town kaydından açıldı, ardından Hyrule Field ve Castle Town dönüşü gözlendi. Bu koşu belirtilen üç ve beş dakikalık bölge matrisini tamamlamadı. Önceki süreçte eş kapsamlı Windows sayaçları yoktu. Bu nedenle tablodan yamanın önce/sonra bellek farkı çıkarılamaz.

## Görüntü, FSR ve devam eden sorunlar

FG kapalı. FSR 4.1.2 RX 6700M üzerinde hem 1536×864 → 1536×864 hem de 1429×804 → 1536×864 dispatch etti. İlk context 5147. karede emekliye ayrıldı ve 5148'de SDK FFX=0 ile imha edildi. Sonraki boyut değişimlerinde de başarılı imha ve ardından yeni dispatch kaydedildi. AMD SDK, temporal girişler ve FSR fallback kodu değişmedi.

Castle Town dönüşüne yakın log hâlâ hazır olmayan çizimleri bildiriyor. İncelenen karede beyaz/yeşil kaplama görülmedi. Bu örnek tüm geçişi doğrulamaz. Önceki 3.710 ms sıçramanın kaynağı izole edilmedi. Geçişte süreç commit artışının hangi tahsis sahibinden geldiğini belirlemek için Windows heap/virtual allocation çağrı yığınları ile renderer kaynak sayaçlarını aynı kare penceresinde eşleştirmek gerekiyor.

Yeni baseline için gerekli görsel doğruluk, eş koşullu A/B, uzun oturum ve tam kaynak kapanışı kanıtı henüz yok. Stabil v0.1.6 yerel kurulumuna dağıtım yapılmadı.

## Kare süresi ve kapanış

Toplam staging oturumu **206 saniye**, çıkış kodu **0**. Windows 1455 bu koşuda tekrarlanmadı. Son süreç örneği 21,32 GiB private commit, tepe 21,83 GiB. Oyun çıktıktan sonraki ayrı sistem örneği 16,81 / 37,39 GiB. Bu düşüş tek tek Vulkan nesnelerinin serbest bırakıldığını kanıtlamaz.

| Ölçüm | Önceki 2524779 raporundaki koşu | 969be74, Castle Town ilk 60 saniye |
| --- | ---: | ---: |
| Oyun kare sayacı | ~27,3/s | ~25,6/s |
| Ortalama ham sunum | 48,07/s | 25,10/s |
| 1% low ham sunum | 4,75/s | 9,90/s |
| P50 / P95 / P99 | 13,08 / 45,94 / 64,86 ms | 36,43 / 64,09 / 86,12 ms |
| En uzun sunum aralığı | 3.710,29 ms | 178,08 ms |
| CPU replay / draw / komut kaydı | 35,52 / 12,91 / 5,00 ms | 39,85 / 14,84 / 5,53 ms |
| CPU pipeline aşaması / bekleme | 0,54 / 0,001 ms | 0,58 / 0,002 ms |
| GPU timestamp ortalaması | 16,73 ms | 18,18 ms |

Farklı cache, kamera ve işletim sistemi koşulları nedeniyle tablo eş koşullu A/B değildir. Oyun sayacı 62,56 saniyede 1.604 kare ilerledi. Ham sunum ölçümü ve oyun sayacı ayrı kaynaklardır. Düzeltilmiş koşu 3,7 saniyelik sıçramayı tekrar üretmedi. Yakın geçiş özeti kare başına 6,5 hazır olmayan çizim kaydetti.

Ölçüm penceresinde device-local heap kullanımı 7.245–7.929 MiB, bütçe 8.671–8.723 MiB. VMA blokları 6.165–6.453 MiB, tahsisleri 4.980–5.896 MiB. Aynı zaman aralığında WDDM ayrılmış 7,06–7,56 GiB, paylaşılan 2,44–3,79 GiB. Renderer telemetrisi sıfır VMA tahsis hatası kaydetti. Host heap örneği 2.501 / 15.301 MiB ve 50 tahsis, toplam 633 MiB idi. Bu sayaçlar birbirine eklenmez.

15 dakikalık kararlılık deneyi, iki ayrı uzun bölge ölçümü, tam worker shutdown/iptal matrisi ve driver seviyesinde yaşam döngüsü testi tamamlanmadı. Mevcut kararlı kurulumun EXE ve DLL hash'leri başlangıçla eşleşti.
