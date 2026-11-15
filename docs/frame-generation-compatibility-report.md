# Windows Vulkan Frame Generation — RX 6700M

## Mevcut yol ve upstream

Shakoquo/Mako HEAD ve projedeki gitlink, karşılaştırmada aynı
`b77ac86187330eb7447ac65ab23187baac4600ca` revizyonunu gösterdi.
`vk_framegen.cpp` Auto modunda Mako optik akışını ve ayrı sunum iş
parçacığını kullanır. Sabit 2× yolunda farklı üreticiler denenebilir;
bu, Auto ile aynı yol değildir. FSR 4.1.2 ve FSR 3.1 upscaling
`vk_fsr4.cpp`, `vk_fsr3.cpp` ve temporal girdilerinden ayrı yürür.
FSR 3.1 FG girdilerinde derinlik ve render pikseli cinsinden geriye
bakan kamera hareketi kullanılır.

Windows recovery yaması, içinde sunulmamış swapchain görüntüleri
bulunan batch'in sonraki acquire'ını 20 ms ile sınırlar. Acquire
başarısızsa yeni görüntü almaya çalışmadan önceden alınan görüntüleri
sunar. Normal bekleme, fence ve semaphore sahipliği değiştirilmedi.
Bu düzeltme tüm donmaları açıklamaz. Önceki FG Off Castle Town
testinde yaklaşık 16 s pipeline derlemesi, Temple of Time OBS
kaydında yaklaşık 45,7 s siyah yükleme görüldü. Temple kaydıyla
eşzamanlı Vulkan logu bulunmadığından bu iki olayın nedeni
eşitlenemez. Eski verilerdeki shader program kimliği de tam pipeline
anahtarının tekrar derlendiğini ispatlamaz.

## SDK seçimi

RX 6700M için sonraki SDK entegrasyon adayı **analitik FG 3.1.6**.
AMD SDK 2.4, Vulkan 1.2 üzerinde bu yolu destekler. ML FG 4.0.2
RX 9000 ve üstünü gerektirir. SDK, uygun donanım dışındaki GPU'larda
analitik sağlayıcıyı seçer. Swapchain 4.0.0 için karşılığı 3.1.7'dir;
bu davranış SDK'nın kendi swapchain yolu entegre edilip Vulkan
format/queue gereksinimleri karşılandığında geçerlidir. Mevcut Mako
swapchain'ine DLL kopyalamak bu yolu etkinleştirmez. AMD'nin Vulkan
swapchain bağlamı için acquire/present fonksiyonları, sunum
senkronizasyonu ve yeniden oluşturmadan önce WaitForPresents birlikte
entegre edilmelidir. Bu aday o swapchain'i eklemiyor.

AMD'nin imzalı Vulkan DLL'leri, resmi SDK paketinden ve varsa
dağıtım koşulları doğrulanarak temin edilir. Bu aday mevcut
`amd_fidelityfx_loader_vk.dll` ve `amd_fidelityfx_upscaler_vk.dll`
dosyalarını kullanır. Gelecekteki resmi FG yolu aynı loader yanında
`amd_fidelityfx_framegeneration_vk.dll` gerektirir. Bu dosya adayda
gerekli değildir ve repoya eklenmedi.

- [AMD SDK 2.4, donanım ve runtime dosyaları](https://gpuopen.com/amd-fsr-sdk/)
- [AMD Vulkan FG yaşam döngüsü ve API](https://gpuopen.com/manuals/fsr_sdk/techniques/frame-interpolation-api/)
- [AMD swapchain entegrasyonu ve sınırlamalar](https://gpuopen.com/manuals/fsr_sdk/techniques/frame-interpolation-swap-chain/)

## Değişiklik ve doğrulama

`patches/fg-incomplete-frame.patch` mevcut pipeline-skip sayacının
her oyun karesindeki değişimini Auto ve sabit FG'ye geçirir. Pipeline
beklerken çizim veya dispatch atlanan kare, kendi gerçek görüntüsünü
normal sırayla sunar fakat sentetik kare üretmez ve sonraki kareye
geçmiş olarak kullanılmaz. Geçerli bir ardışık çift oluşunca
interpolasyon döner. Upscaling, açılan 20 ms sınırı, strict pipeline
politikası ve GPU senkronizasyon zinciri korunur.
`scripts/Build-LocalGame.ps1` yamayı otomatik uygular.
`test_framegen_gate.py` iki kayıt yolunu ve iki geçmiş yolunu
kontrol eder.

Windows x64 Vulkan DLL derlemesi başarılı, 0 derleme hatası.
Altı yama temiz upstream çalışma ağacında normal build sırasıyla
uygulandı. FG gate, Auto pacing, present-ahead, device-loss ve temporal
history testleri geçti. Device-loss testindeki ilk Windows çalıştırması
toolchain runtime DLL arama yolu nedeniyle başarısız oldu; doğru
toolchain PATH ile tekrar geçti.

## Staging ve geri dönüş

Staging, çalışır EXE'nin kopyası ve yeni Vulkan DLL ile
`D:\codex\OOT-REMAKE-AMD\fg-incomplete-staging\hookshot.exe`.
Save, ayarlar ve cache ayrı kopyalardır. Yerel kurulum deploy edilmedi.
Adayı kapatıp mevcut yerel EXE'yi açmak geri dönüş için yeterlidir.
`Switch-InstalledBuild.ps1` runtime kapsamı olan EXE ile Vulkan DLL'i
SHA-256 manifesti üzerinden geri alır. Bu görevde çalışan kurulumda
gerçek deploy/restore çevrimi yapılmadı. AMD DLL'leri değiştirilmedi.

Kontrollü testte aynı save ve rotayı, aynı iç/çıkış çözünürlüğü,
VSync ve FPS limitiyle dört kez çalıştırın. FSR 4.1.2 ve 3.1 için
birer FG Off ve FG Auto koşusu. Temple of Time yüklemesinden ilk
harekete geçişi ve Castle Town girişini ayrı kaydedin. Temel FPS,
generated FPS, present FPS, P95/P99, acquire/present ve pipeline
beklemesini ayrı değerlendirin. Sayaçtaki toplam FPS, temel FPS yerine
kullanılmamalıdır. Geometri, ghosting ve kamera kesmesi sırasında
görüntü gözlemi gereklidir.

## RX 6700M staging smoke testi

14:14–14:16 UTC kaydı, gerçekte Hyrule Field save'ini yükledi ve
kontrol arayüzüyle Castle Town'a geçti. Capture'ın elle girilen
`Scene` etiketi Temple of Time idi; oyun haritası ve save kaydı
esas alındı. Ayarlar FG Auto (Built-in), FSR 4.1.2, VSync açık,
FPS limiti kapalı, 1920×1080 seçili çıkış ve 1280×720 pencere.
Provider logu 1536×864 → 1536×864 dispatch'i doğruladı. Auto,
144 Hz sunum hattını başlattı. SDK 3.1.6 FG dispatch'i denenmedi.

Hyrule Field'da kontrol arayüzü bir örnekte 36,2 FPS bildirdi.
Castle Town'a geçiş frame 2191'de onaylandı. Son kontrolde oyun
yine 2191'deydi ve 0 FPS/stalled bildiriyordu. Aynı sırada sunum
iş parçacığında 3.004 ms'ye varan grafik pipeline derlemeleri
loglandı. Bu koşuda deferred-acquire batch kesintisi loglanmadı.
Kontrol komutuyla kapatma exit 0 döndürdü.

CSV'deki 5.533 karışık sunum aralığı 81,15 ortalama sunum FPS,
14,55 ms P95 ve 22,34 ms P99 verdi. Menü ve yükleme dahil
olduğu için bu rakamlar sahne performansı veya kıyas sonucu
olarak kullanılmaz. CSV son takılmayı tamamlanmış sunum aralığı
olarak kaydetmedi; 132,17 saniyelik süreçte 68,18 saniyelik
sunum zaman çizelgesi var. Bu araçta render ve generated FPS
ayrı sayılmadı. Tam matris, GPU/acquire ayrıştırması ve görüntü
kalitesi karşılaştırması açık. Castle Town donması çözülmüş
kabul edilemez, bu nedenle çalışan kurulum ya da kararlı paket
güncellenmedi.
