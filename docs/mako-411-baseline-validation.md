# Mako 4.1.1 kararlı oyun testi

Bu test ilk kurulu Mako 4.1.1 ikililerinin RX 6700M üzerindeki
davranışını, sonraki adaylarla karşılaştırmak içindir. Kaynak ve
SHA-256 bilgisi [kaynak kaydında](recomp-source-provenance.md).

## Koşullar

- Windows 11 x64, Ryzen 7 5800H, Radeon RX 6700M, Vulkan.
- İlk yerel EXE ve DLL SHA-256 doğrulandı. Bu test için derleme yapılmadı.
- Staging, ilk kararlı yedeğin cache kopyasını (10.253.707.329 bayt
  düzenli dosya, yarım yazılmış temp dosyaları hariç) ve güncel
  kurulumun save kopyasını kullandı. RomFS yerel kaynağına bağlıydı.
- FG Off, VSync açık, FPS limiti kapalı, 1920×1080 seçili çıkış,
  1280×720 pencere, 1536×864 Native AA.
- Pipeline skip/probe test override'ları kapalı, kararlı renderer
  varsayılanları geçerli. RX_VK_FRAME_TRACE yalnız ölçüm için açık.
- Önce Castle Town save'i yüklendi. Ardından Hyrule Field ve Castle
  Town dönüşü yerel kontrol arayüzünden tetiklendi. Bu test aynı
  konsol komutuyla tekrarlanabilir. Castle Town dönüşünden sonra
  ölçüm sabit kamera koşulunda alındı.

Tekrarda ilk doğrulanmış cache kopyasından başlayın. Aynı save,
pencere, FSR, FG ve VSync ayarlarını kullanın. Menü ve başlangıç
precompile sürelerini gameplay penceresinden ayrı tutun.
Son sunumdan sonra takılma varsa tek başına present CSV
yeterli değildir. Sahne, kare ilerlemesi ve sunum CSV zamanını
duvar saatiyle birlikte örnekleyin.

Bu ölçüm için güncel OOT capture/ölçüm betikleri ve Mako yerel
kontrol istemcisi kullanıldı. Bunlar test edilen EXE veya DLL'i
değiştirmedi. Save, cache, ROM ve ham oyun kayıtları depoya eklenmez.

## RX 6700M sonucu

FSR 4.1.2 provider dispatch'i 1536×864 → 1536×864 olarak
doğrulandı. Market save'i açıldı ve Market → Hyrule Field → Market
geçişleri logda doğrulandı. Dönüşte ilk izlenen oyun kare sayacı
3346, kapanmadan önceki son canlı örnek 4335'ti. Dönüş sonrasındaki
canlı örneklerin hiçbiri stalled değildi. Ardından log pencerenin
kapandığını ve süreç çıkış kodu 0'ı kaydetti. Kapanışın nedeni
kayıttan belirlenemedi.

Dönüşten 31,7 s sonra alınan tek görüntüde beyaz-yeşil kaplama
veya belirgin eksik geometri görülmedi. Hareketli kamera ve
temporal artefaktlar bu tek kareyle değerlendirilemez.

Hedef 30 s ısınma + 60 s ölçümdü. Capture CSV aralığı yaklaşık
171,47–227,64 s oldu. 932 mevcut aralık yaklaşık 56,17 s kapsadı.
Bu nedenle aşağıdaki sonuçlar kısmi referanstır.

| Ölçüm | Sonuç |
| --- | ---: |
| Ortalama present FPS | 16,59 |
| 1% low | 4,86 FPS |
| P50 / P95 / P99 present süresi | 60,74 / 100,13 / 147,79 ms |
| En uzun present aralığı | 281,27 ms |
| 33,3 / 50 / 100 ms üzeri | 756 / 660 / 48 |
| Oyun kare sayacı (ısınma sonrası, 52,02 s) | 665 kare, yaklaşık 12,79 FPS |

Present CSV ve oyun/replay kare sayacı farklı noktaları ölçer.
Bu koşuda FG kapalıydı. Present ortalaması oyun render FPS'si
olarak kullanılmadı.

Isınma sonrası ilk ve son canlı örneğin arasındaki 666 renderer
trace satırında `pipe_wait_ms` toplamı ve maksimumu 0,00 ms.
`memsync_ms` ortalaması 13,55 ms, `late_wait_ms` 12,17 ms,
`pipelines_ms` 0,61 ms. Bu zamanlar örtüşebilir ve toplanmadı.
Castle Town dönüşünden önceki Hyrule geçişinde sunum
iş parçacığında yavaş pipeline derlemeleri görüldü. Castle Town
dönüşünün başında ise bir worker derlemesi 4,48 s sürdü.
Sonraki sabit sahnede düşük FPS ile strict pipeline beklemesi
aynı bulgu olarak görülmemeli.

Vulkan device-local örneklerinden biri 8.369 MiB usage /
8.369 MiB dinamik budget, VMA 5.517 MiB block ve 4.752 MiB
aktif allocation gösterdi. WDDM'de yük taşıyan adaptörün
dedicated ve shared ölçüm maksimumları ayrı ayrı 8,23 ve
4,56 GiB oldu. Bunlar fiziksel kapasite veya toplanabilir
değerler değildir. Kaydedilen örneklerde nihai VMA tahsis
hatası yok. Compaction ve geç GPU sayfa beklemeleri
görüldü. Başka koşular olmadan tek kök neden ataması yapılmaz.

Kararlı 30 FPS hedefi bu koşuda karşılanmadı. Bir sonraki A/B,
aynı kaynak ve save ile memory sync, late pages ve bütçe
baskısını ayrı ölçmeli. Bu dal deneysel runtime değişikliği
içermez. Temple of Time ve FG Auto bu ilk testin kapsamında değildi.
