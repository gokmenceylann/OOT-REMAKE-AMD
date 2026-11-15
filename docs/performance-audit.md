# RX 6700M performans denetimi

Mako 4.1.1, Windows x64 ve Vulkan. Tanılama yaması shader çeviricisini,
FSR provider seçimini ve kaynak ömrü politikasını değiştirmez. Shader damgası
`fe6b0a1d7ec998de` olarak kaldı. Yama, `-EnablePerformanceAudit` ile derlenir.
Çalışma zamanında `RX_VK_PERF_AUDIT=1`, her 120 oyun sunumunda bir ölçüm satırı açar.

## CPU ve GPU

`vk_replay.cpp` içindeki replay sayaçları, komut hazırlama, draw, descriptor,
upload ve misafir bellek eşitleme işlerini örnekler. Replay süresi host tarafının
duvar saati süresidir. İçindeki bellek eşitleme süresini tekrar toplamaya katmayın.
`HOS_PROFILE=5` thread kullanımını bir çekirdeğin yüzdesi olarak beş saniyede
bir örnekler. Recompiler'ın kendi maliyeti ve ana oyun thread'inin kare
kritik yolu için ayrı örnekleme gerekir.

GPU süresi, tamamlanan komut tamponlarının Vulkan timestamp toplamıdır.
`gpu_recordings` geçerli timestamp sayısıdır. Sıfır örnekli pencereyi GPU süresi
olarak kullanmayın. GPU işi sıradaki tampon tamamlandığında okunur. CPU ve GPU
paralel ilerleyebileceği için süreler toplanmaz. Present çağrı süresi ile
Present CSV'deki kare aralığı farklıdır. Draw ve pass sayıları iş yükü
göstergeleridir. Geometri üçgen sayısı henüz ölçülmüyor.

## Mevcut kayıtların gösterdiği

Eski karışık Mako 4.1.1 yerel kaydında en ağır örneklerden biri yaklaşık
2.811 draw ve 214 pass içeriyor. CPU replay 56,71 ms, bunun içindeki bellek
eşitleme 22,32 ms, GPU 46,6 ms ve Present çağrısı 0,39 ms. Aynı oturumdaki bir
yerel Vulkan heap örneği 8.722 / 8.722 MiB, VMA blokları 6.141 MiB ve aktif VMA
tahsisleri 5.250 MiB gösterdi. WDDM dedicated/shared okumaları ve fiziksel
bellek kapasitesi bunlardan ayrıdır. O pencerenin bölgesi bağımsız olarak
etiketlenmedi.

Yeni DLL ile ayrı save açılışında 120 sunumluk bir oyun penceresinde 2.825,5
draw ve 227,1 pass, CPU replay 33,119 ms, bellek eşitleme 5,174 ms ve GPU
22,453 ms kaydedildi. 4.081 GPU kaydı geçerliydi. Bu örnek, CPU replay'in
birincil aday olduğunu ve GPU'nun da 16,67 ms bütçeyi aştığını gösteriyor.
Castle Town ile Hyrule Field için eş süreli rota veya geometri miktarı henüz
ölçülmedi. Siyah ekran ve beyaz-yeşil bozulma bu kurulum testinde görsel olarak
değerlendirilmedi.

## FSR

RX 6700M, FSR 4.1.2 Native AA için 1536×864 → 1536×864 dispatch yaptı.
286 GPU örneğinde Mako giriş hazırlama 0,203 ms, SDK dispatch 4,368 ms ve
Mako çıkışı 0,022 ms ortalamasındaydı. SDK dispatch P95 6,001 ms ve P99
8,173 ms ölçüldü. Pass timing ek GPU eşitlemesi kullanır. Bu dağılım
profil açıkken geçerlidir. FSR 3.1 ve FSR 4.1.2 Quality için aynı rota
karşılaştırması henüz yapılmadı.

## Eş koşullu rota

Frame Generation Off, aynı V-Sync, FPS limiti, çıkış çözünürlüğü, save,
grafik ayarları ve kamera rotası kullanın. Castle Town ve Hyrule Field için
ısınmadan sonra ayrı 60 saniyelik pencereler alın. FSR 3.1, FSR 4.1.2
Quality ve Native AA'yı ayrı koşun. Menü seçimiyle gerçek dispatch'i log
üzerinden karşılaştırın. İlk koşuda `-PassTiming` eklemeden oynanış sürelerini
kaydedin. Ayrı koşuda GPU pass ve FSR span ölçümü için `-PassTiming` ekleyin.
Ortalama FPS, P95 ve P99, `session-summary.json` içinde bulunur.

~~~powershell
.\scripts\Capture-VulkanSession.ps1 -GameDirectory 'D:\OOT-REMAKE-AMD-local\game' `
    -OutputDirectory 'D:\codex\castle-town-fsr4-quality' -Scene 'Castle Town / FSR 4 Quality' `
    -PerformanceAudit -SkipSeconds 30 -DurationSeconds 60
~~~

`SkipSeconds` ölçüm başlangıcına göre örnektir. CSV saati ilk Present'te
başlar. Bölge, seçilen rota ve test anında doğrulanmalıdır. Oyun açıldıktan
sonra rotayı kaydet, ardından pencereyi kapat. VRAM satırları, VMA ve isteğe
bağlı WDDM örnekleri ayrı tutulur. Başlangıç ve geçiş pencerelerini rota
özetine karıştırmayın.

## İlk üç inceleme adayı

1. CPU replay ve bellek eşitleme. Ağır pencerelerde sync kopyalarını,
   descriptor hazırlığını ve timeline beklemelerini ayrı ölçün.
2. GPU geometri ve pass maliyeti. En ağır pass'leri GPU profiliyle ölçün
   ve gerçek FSR dispatch maliyetini scaler karşılaştırmasında ayırın.
3. VRAM bütçesi ve geçiş kaynakları. Heap limitine yaklaşan pencerelerde
   kaynak geçişlerini, texture yüklemeyi ve pipeline kuyruğunu eşleştirin.

Optimizasyon uygulanmadı. Windows x64 renderer derlendi, ayrı kopyada
save açılışı ve FSR Native AA doğrulandı. Yedekleme, kurulum ve geri dönüş
sentetik bir dizinde sınandı. Yerel geçiş yalnızca değişen EXE/DLL dosyasını
değiştirir. Bu test sürümünde EXE aynı kaldı ve yalnızca Vulkan DLL güncellendi.

## Geri dönüş

Oyun kapalıyken `Switch-InstalledBuild.ps1 -Restore` çalıştırın. Betik doğrulanmış
yedekten runtime ikililerini yükler. Save, cache ve ayarları geri yazmaz.

~~~powershell
.\scripts\Switch-InstalledBuild.ps1 -GameDirectory 'D:\OOT-REMAKE-AMD-local\game' `
    -BackupDirectory 'D:\codex\OOT-REMAKE-AMD\Backups\OOT-REMAKE-AMD-2026-11-15_132736862' -Restore
~~~
