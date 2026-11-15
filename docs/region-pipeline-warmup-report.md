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
