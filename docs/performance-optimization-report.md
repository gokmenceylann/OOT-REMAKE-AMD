# RX 6700M pipeline performans optimizasyonu

## Değişiklikler

- `patches/pipeline-performance.patch`, Mako'nun Vulkan çizim kodunu ve cache
  dosyası katmanını günceller. Windows mevcut hedefi korurken bir geçici cache
  dosyası için gereken alanı önceden kontrol eder. Yer yetersizse yazım
  başlamaz. Oyun kaynakları veya geçerli cache dosyaları silinmez.
- Windows AMD'de `RX_VK_PIPE_SKIP=0` ve `RX_VK_PIPE_PROBE=1` geçerliyse renderer tam grafik
  pipeline'ını önce Vulkan cache'inden derleme yapmadan ister. Hazır bir
  pipeline bulursa onu doğrudan kullanır ve worker işini kuyruğa eklemez.
  Cache miss normal worker ve bekleme yolunu izler. Bu sorgu varsayılan kapalıdır.
- Optimizasyonsuz hızlı derleme adayında bazı işler 1,5 saniyeyi aştı.
  Ara koşu 60 saniyelik ortak pencereyi tamamlamadan normal kapanış yaptı.
  Bu deneysel yol kurulan sürüme alınmadı.
- `Build-LocalGame.ps1` yamayı uygular. `Capture-VulkanSession.ps1` içindeki
  `-SampleGuestThread 'sead::MainThread'` ayrı bir profilde ana oyun
  thread'inin stack örneklerini `guest-stacks.txt` içine yazar. Bu örnekler
  EXE ve renderer linker haritalarıyla adlandırılabilir. Kare başına kesin
  AArch64 çalışma süresini doğrudan vermezler. Stack örneklemesini FPS
  karşılaştırmasından ayrı koşun.

## Kanıt ve sınırlar

Castle Town kaydında 633 bekleyen iş ve 14,95 saniyelik bir Vulkan pipeline
derlemesi görüldü. Logdaki aynı shader program kimliği birden fazla
pipeline durumu için geçerli olabileceğinden tekrarlanan program
kimlikleri, birebir aynı pipeline'ın yeniden derlendiğini kanıtlamıyor.
Mako aynı replay pipeline anahtarını mevcut giriş üzerinden paylaşıyor.
Önceki testte diskte yarım kalmış yaklaşık 1,5 GB cache geçici dosyası
görüldü. Düşük boş alan kontrolü yeni geçici dosya açılmasını önler.
Canlı cache ve yarım kalmış dosya korunmuştur.

Bellek eşitleme, Vulkan bariyerleri, FSR 4.1.2, FSR 3.1 fallback,
motion vectors, temporal history ve Frame Generation sunumu bu yamada
değiştirilmedi. Bellek eşitlemede 5,174 ms referansa göre kazanç ve
Castle Town ile Hyrule Field arasındaki eş koşullu GPU farkı henüz
ölçülmedi.

## Kurulum ve geri dönüş

Bu sürüm yalnızca `hookshot_vk.dll` değiştirir. Shader damgası
`fe6b0a1d7ec998de` olarak kaldı. `Backup-InstalledBuild.ps1` alınan
snapshot'ı SHA-256 ile doğruladı. `Switch-InstalledBuild.ps1 -Restore`
oyun kapalıyken önceki ikilileri yükler. Save, ayar ve cache dosyalarını
geri yazmaz.

~~~powershell
.\scripts\Switch-InstalledBuild.ps1 -GameDirectory 'D:\OOT-REMAKE-AMD-local\game' `
    -BackupDirectory 'D:\codex\OOT-REMAKE-AMD\Backups\OOT-REMAKE-AMD-2026-11-15_141003850' -Restore
~~~

Görsel kontrol için oyunda aynı Castle Town ve Hyrule Field rotalarını
Frame Generation Off, aynı FSR modu, aynı render çözünürlüğü, V-Sync ve
FPS limiti ile koşun. Bu testte oluşabilecek uzun beklemeleri ve
beyaz-yeşil bölgeleri kayıt zamanlarıyla birlikte not edin.

## Karşılaştırma ve deneyden çıkarılan kod

Aynı izole save ve dosya cache kopyasından çıkan sabit kamera
koşusunda temel DLL, ölçülen 60 saniyelik pencerede 35,73 FPS, P95 32,50
ms ve P99 36,50 ms verdi. Dolaşma rotası kaydedilmedi. Hızlı derleme açık
deney 60 saniyelik pencereyi tamamlamadı. Cache'den cevaplanan en az 1.000
pipeline görüldü. Optimizasyonsuz derleme örnekleri 239,9–1.591,2 ms sürdü.

Kuyruktan önce cache sorgusu açık aday en az 600 hazır pipeline'ı
kuyruğa eklemeden kullandı. Aynı nominal 60 saniyelik pencerede
yakalanan 201 sunum aralığında ortalama 11,21 FPS ve P99 1.325,54 ms
görüldü. Logda iki tam pipeline derlemesi 16 saniyeyi aştı. Uzun
bekleme ve eksik sunum nedeniyle bu örnekler 60 saniye korunmuş FPS
artışı olarak yorumlanmaz. Cache sorgusu bu nedenle varsayılan kapalı
bırakıldı. İsteğe bağlı `RX_VK_PIPE_PROBE=1` ile araştırılabilir.
Disk alanı denetimi varsayılan olarak çalışır.

Windows x64 renderer derlendi. Pipeline cache testi 187 doğrulama ve 11
I/O hata aşamasından geçti. Hızlı pipeline karar testi ön deneyde geçti.
Yayın adayı o deneysel değişiklikleri içermez.

## RX 6700M üzerinde son doğrulama

Varsayılan ayarlarla derlenen DLL, yalıtılmış save ve cache kopyasıyla
gerçek oyunda çalıştırıldı. Save yüklemesi tamamlandı. Vulkan logu, FSR
4.1.2'nin 1536×864 → 1536×864 Native AA dispatch'ini doğruladı. Frame
Generation kapalı, cache sorgusu kapalı ve sıkı pipeline bekleme
politikası açıktı.

Otomatik geçişte oyun `Market_Child` (Castle Town) haritasına ulaştığını
bildirdi. Ardından sunulan kare sayacı 2449'da takıldı ve kontrol
arayüzü 0 FPS ile `stalled: true` bildirdi. Sunum iş parçacığı logunda
16.068 ms süren bir pipeline derlemesi var. Hyrule Field'a dönüş
komutları zaman aşımına uğradı. Bu gözlem donmanın bütün nedenlerini
tek başına kanıtlamaz. Görsel kararlılık ve karşılaştırmalı rota
performansı doğrulanamadı.

Çalışan kurulumun dosyalarına dokunulmadı. Son aday Installer veya
kararlı Release olarak yayımlanmadı. Yeni Frame Generation SDK
entegrasyonu, tamamlanmış oyun testi koşuluna bağlı olarak bekliyor.

## Yerel kurulumda Temple of Time (15 Kasım 2026)

RX 6700M üzerindeki 2:17 OBS kaydında Temple of Time save'i açıldı.
Video zamanına göre 00:05.67–00:51.33 arasında oyun alanı siyahtı
(45,67 saniye). Görüntü geldikten sonra takılmalar sürdü. Örneğin
01:17.00–01:31.43 aralığında, FG Auto açıkken, ekranın orta bölümünde
14,43 saniye boyunca çok az görüntü değişimi ölçüldü. Bu ölçüm
FFmpeg blackdetect/freezedetect ve kare örneklerine dayanır.
Hareketsiz sahneler de freezedetect'e takılabildiğinden bu süreler
Vulkan present veya GPU bekleme süresi olarak kullanılmaz.

Çıkış menüde 1920×1080 görünüyordu. Kayıt içinde FSR 3.1 ve FSR 4,
1536×864 ve 1408×792 iç çözünürlükler, ayrıca FG Auto (Built-in FG)
ve Off kullanıldı. Bir örnekte yaklaşık 52 temel FPS ve 144 sunulan
FPS vardı. FG kapalı sonraki kesitte sayaç yaklaşık 53–58 FPS gösterdi.
Bu değerler tekil gözlemlerdir. Ayarlar değiştiği için eş koşullu
FSR karşılaştırması veya P95/P99 çıkarılamaz. Menüdeki FSR 4 seçimi,
gerçek SDK provider dispatch'ini tek başına doğrulamaz.

### Açık sorun ve sonraki ölçüm

Save yüklemesindeki uzun siyah bekleme ve sahne içi takılmalar açık.
Önceki otomatik Castle Town denemesinde FG kapalıyken 16 saniyeyi
bulan pipeline derlemesi kaydedildi. Temple of Time videosu için
eşzamanlı renderer logu olmadığı için aynı neden henüz doğrulanamadı.

Bir sonraki ölçümde aynı Temple of Time save'i ve rota, aynı FSR ve
iç çözünürlük ile önce FG Off, sonra FG Auto çalıştırılacak. İlk kontrol
save onayından ilk oynanabilir kareye kadar geçen süreyi, sonraki
kontrol aynı hareket rotasındaki present aralıklarını karşılaştıracak.
'Capture-VulkanSession.ps1 -PerformanceAudit' çıktısında uzun
graphics pipeline ve job wait süreleri, Vulkan acquire/present
beklemeleri ve gerçek FSR provider dispatch'i kayıtla eşleştirilecek.
'RX_VK_PIPE_SKIP=0' mevcut çalışmada korunur. Bu ayarı değiştiren deney
ayrı kopyada yapılmalıdır, çünkü atlanan draw'lar önceki beyaz-yeşil
yüzey sorununu yeniden ortaya çıkarabilir.
