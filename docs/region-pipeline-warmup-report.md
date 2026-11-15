# Bölge bazlı Vulkan pipeline hazırlığı

En son eklenen 64 kaydı önceden hazırlamak Castle Town'da ihtiyaç
duyulan pipeline'ların tamamını kapsamadı. Bölge profili, aynı bütçeyi
o bölgenin önceki çalıştırmada sunum iş parçacığında en uzun süren
tam pipeline anahtarlarına ayırır.

`Export-RegionPipelineProfile.py` mevcut renderer logundan hedef harita
ve başarılı yavaş pipeline oluşturma kayıtlarını okur. Doğrulanmış bir
teleport için varışa kadarki anahtarları da dahil eder. Anahtarları
tekilleştirip en uzun ölçülen süreye göre sıralar. Arka plan
worker'larında görülen anahtarlar ve başarısız Vulkan sonuçları bu
sürümde profil girdisi değildir. Logda yeterli kanıt yoksa kayıt
üretilmez. Tam dosya, cache dizinindeki geçici dosyaya yazıldıktan
sonra atomik olarak değiştirilir. Oyun çalışırken dosya üretilmesi
gerekmez.

Renderer yalnızca üç tanınan bölge adından birini kullanır.
Profil sürümü, Vulkan vendor/device kimliği ve sürücü sürümü
doğrulanır. Profil tek başına pipeline oluşturamaz. Anahtar, Mako'nun
derleyici damgasını doğruladığı yerel pipeline notlarında bulunmalı.
Eksik, uyumsuz veya eşleşmeyen profil normal başlatmayı engellemez.
Geçerli anahtarlar mevcut iki worker'lı başlangıç hazırlığında
işlenir ve runtime tablosunda yeniden kullanılabilir.

Bu sürümde bölge başlatmadan önce seçilir. Oyun içindeki bölge
değişimini tahmin edip arka plan hazırlığı başlatan bir yol yok.
Yeni ve profilde olmayan zorunlu pipeline'lar strict modda sunumu
bekletebilir. Draw atlama ve FG/FSR davranışı değiştirilmedi.
Aynı sahne ve donanımda görsel doğrulama ile 30 FPS hedefi
tamamlanana kadar bu yol opt-in kalır.

## Yerel test

Castle Town için gerçek kayıtla örnek. Aynı komut
`HyruleField` ve `TempleOfTime` değerlerini de kabul eder.
Her profili ilgili bölgeyi ve pipeline derlemesini içeren logdan
üretin.

~~~powershell
& $python .\scripts\Export-RegionPipelineProfile.py --log "$capture\renderer.log" --cache-directory "$stage\cache" --region CastleTown
$env:RX_VK_PRECOMPILE_REGION = 'CastleTown'
$env:RX_VK_PRECOMPILE_RECENT = '64'
.\scripts\Capture-VulkanSession.ps1 -GameDirectory $stage -OutputDirectory $out -Scene 'Castle Town'
~~~

Normal başlangıca dönmek için iki deney değişkenini kaldırıp EXE'yi
yeniden başlatın. Save ve kurulu cache değişmez. Profil ve capture
dosyaları yerel test çıktılarıdır.

## Doğrulama

Windows x64 Vulkan renderer derlemesi geçti. İlk denemede
`cache_path` çağrısının `const char*` imzası düzeltildi, sonraki
derleme sıfır hatayla tamamlandı. Yama önceki patch dizisi üzerine
kontrol edildi. Python regresyon testleri geçerli geçişin öncesi ve
sonrasındaki anahtarların seçilmesini, tekilleştirmeyi, sahne dışı
anahtarların elenmesini, doğrulanmamış geçişi ve karışık aygıt
kayıtlarının reddini kontrol etti.

Önceki gerçek RX 6700M oturumundan Castle Town için 28 anahtar
çıktı. Renderer 2.116 doğrulanmış not arasından 28'ini eşleştirdi.
Açılış ön hazırlığı 440 ms sürdü. Bunun 340 ms'si cache ve notların
okunmasıydı. Önceki son-eklenen-64 denemesi 27,7 s idi. Hazırlanan
iş sayısı ve başlangıç cache içeriği farklı olduğundan süreler
eş koşullu performans karşılaştırması değildir. Hyrule Field için
bu kaynak log, doğrulanan harita aralığına ait yavaş anahtar
üretmedi. Temple of Time için eş koşullu capture gerekir.

### Oyun içi sonuç

FG Off, FSR 4.1.2 Native AA 1536×864 ve strict çizim bekleme
koşusunda Hyrule Field save'i açıldı. FSR provider dispatch'i
RX 6700M üzerinde kaydedildi. Castle Town'a geçiş kabul edildi,
ardından çıktı 2577. karede ve 0 FPS'te takıldı. Ekran görüntüsü
isteği zaman aşımına uğradı. Kaynak logdan seçilen 28 anahtar,
bu oturumdaki 31 yavaş derleme anahtarının hiçbirinde tekrar
görülmedi. Yeni yavaş derlemelerin toplamı 32.419 ms, en uzunu
2.302 ms oldu. Log bir mesh fallback draw'unun compute pipeline
beklerken atlandığını da kaydetti. Görsel bütünlük doğrulanamadı.

Menü ve yükleme dahil 2.579 aralıkta 32,75 ortalama FPS, 0,80
1% low, P50/P95/P99 16,77/30,10/59,46 ms ve 14.857 ms maksimum
görüldü. 33,3/50/100 ms üzeri aralıklar sırasıyla 87/33/17.
Son donma CSV'de tamamlanmış bir aralık olarak yer almadı.
Bu değerler kararlı 30 FPS veya eş koşullu rota performansı değildir.

84 WDDM örneğinde yük taşıyan adaptörün dedicated ve shared
maksimumları ayrı ayrı 7,43 ve 3,20 GiB oldu. Vulkan'da bir
örnekte 5.708 MiB usage / 9.426 MiB budget, VMA'da 4.408 MiB
block / 2.653 MiB allocation ve sıfır nihai tahsis hatası
görüldü. Farklı kapsamlı sayaçlar toplanmadı. Bu koşu GPU
doluluk oranı, worker lock süresi veya 45/60 FPS hedeflerini
doğrulamıyor. FG Auto ve Temple of Time rota testleri tamamlanmadı.

Bölge profili bilinen anahtarları öne alır. Tek bir rota
gözlemi sonraki koşunun tüm pipeline varyantlarını kapsamaya
yetmedi. Uzun compile miss'leri sunumun kritik yolunda
kaldığından kalıcı düzeltme ve kararlı Release yok.

## Pipeline kullanımı üzerinden öğrenme

`patches/pipeline-region-use.patch` isteğe bağlı
`RX_VK_PIPE_REGION_TRACE=1` ile graphics draw ve compute dispatch
kaydının ardından anahtar yayınlar. Graphics tam pipeline anahtarını,
compute program ve varyant çiftini kaydeder. Her replay thread'i
aynı anahtarı 60 karelik pencerede bir kez yazar. Ayrı profiling
geçişinde kullanılır. CPU ve log maliyeti nedeniyle bu ölçümle
normal oturum FPS'si karşılaştırılmaz. FSR gibi renderer'ın kendi
compute efektleri ve mesh fallback yardımcı dispatch'leri bu
profilin kapsamında değildir.

Exporter, doğrulanmış harita aralığındaki kullanım ve önceki yavaş
derleme kayıtlarını birleştirir. Birden fazla `--log` ve isteğe
bağlı `--age child|adult` kabul eder. Tüm gözlenen anahtarları
profilde tutar. Yavaş derlemelere, ardından compute kayıtlarına
ve farklı oturumlarda tekrar görülen graphics kayıtlarına öncelik
verir. Bir GPU ve sürücü kimliği dışındaki birleşimleri reddeder.
Atomik dosya yazımı ve eski profil başlığı korunur. Eski renderer
compute satırlarını tanımaz, graphics satırlarını okuyabilir.

Açılış renderer'ı ilk 256 profil satırından, başlangıç limitini
aşmadan eşleşme arar. En fazla 16 compute varyantı talep edilir.
Compute yalnızca doğrulanmış yerel program cache içindeki aynı
anahtar ve varyantla hazırlanır. Mevcut worker önce Vulkan cache
yolunu dener ve yalnız geçerli pipeline yayımlar. Motion vectors,
FSR, FG ve swapchain zinciri değiştirilmedi.

### Kritik yoldaki bekleme

`graphics_pipeline` hızlı lookup ve tam anahtar tablosunu kullanır.
Eksik kayıt için oluşturulan tek `PipeEntry`, worker sonucu
hazır olana kadar beklenir. Strict modda `draw` çağrısı
`jobs_wait` üzerinden işi kuyruktan devralabilir. Worker işi
almışsa süre sınırı olmayan koşul değişkeni beklemesi vardır.
Compute yolunun isteğe bağlı kısa beklemeleri ile zorunlu
mesh fallback işlerindeki beklemeler farklıdır. Aynı shader
programı da birden çok graphics pipeline varyantına sahip
olabilir. Güvenli command replay veya sahne giriş planı olmadan
zorunlu çizim için bu beklemeyi kesmek görüntü ve kaynak
doğruluğunu bozabilir. Bu yama bekleme veya kapatma sözleşmesini
değiştirmez. Oyun içi otomatik ön hazırlık ve yeni compile
miss'ini kritik yoldan çıkaran planlama henüz yok.

Windows x64 Vulkan DLL sıfır hatayla derlendi. Sabit upstream
üzerine önceki yamalarla uyumluluk ve üç exporter testi geçti.
Testler doğrulanmış geçişi, başarılı kullanımı, anahtar
tekilleştirmesini, yaş filtresini ve farklı sürücü kayıtlarının
birleştirilmemesini kapsar. Otomatik Vulkan queue/lifetime
regresyonu bu değişiklik için eklenmedi.

### RX 6700M kullanım profili ve tekrar açılış testi

FG Off, strict bekleme ve 1536×864 FSR 4.1.2 Native AA
kullanıldı. Kullanım kaydı Castle Town çocuk profiline
1.046 graphics ve 95 compute, Hyrule Field çocuk profiline
664 graphics ve 86 compute anahtarı verdi. Castle Town profili
bir eski ve bir yeni oturumdan birleşti. Hyrule Field profili
tek yeni oturumdan geldi. Temple of Time profili oluşmadı.

İlk koşuda Hyrule Field açıldı ve Castle Town'a giriş
doğrulandı. Sunum 2282. karede durdu. Görüntü isteği zaman
aşımına uğradı. WDDM'nin yoğun adaptörü 76 örnekte ayrı
maksimumlar olarak 7,52 GiB dedicated ve 3,21 GiB shared
gösterdi. CSV'deki menü ve yükleme dahil 2.293 aralıkta
P50/P95/P99 16,71/28,72/74,62 ms ve maksimum 15.197 ms.
Bunlar profiling aralıklarıdır.

Yeniden başlatmada gerçek Castle Town profili 48 graphics
ve 16 compute seçti. Hazırlık 442 ms sürdü. Log, 16 compute
pipeline'ın da Vulkan cache'den geldiğini ve 0 yeni compute
derlemesi yapıldığını doğruladı. Oyun içi FSR 4.1.2 dispatch'i
yeniden görüldü. Castle Town'a giriş kaydedildi ancak sunum
1696. karede durdu. Sunum iş parçacığında 23 yavaş derleme,
toplam 30.543 ms ve maksimum 2.923 ms kaydedildi.
Karışık 1.679 present aralığında P50/P95/P99
16,83/35,29/105,17 ms ve maksimum 4.753 ms. Son donma
bu dağılımda tamamlanmış aralık olarak yok. Bir 60 saniyelik
sahne ölçümü veya önce/sonra FPS kazanımı doğrulanmadı.

Ayrı EXE
`D:\codex\OOT-REMAKE-AMD\pipeline-region-use-staging\hookshot.exe`.
Mevcut kurulum veya kararlı Release güncellenmedi. FG Auto,
Temple of Time, tam geçiş matrisi ve görsel doğruluk açık.
