# RX 6700M Vulkan stutter — kök neden incelemesi

## Doğrulanan neden

FG Auto testindeki kullanıcı logunda sunum iş parçacığında sekiz
300 ms üzeri pipeline derlemesi görüldü (toplam 5.146 ms, en uzun
1.201 ms). Oyun daha sonra normal pencere kapanışı kaydetti.

Yeni anahtar tanılamasıyla FG Off açıkça test edildi. Hyrule Field
save'i yüklendi, FSR 4.1.2 1536×864 Native AA dispatch'i doğrulandı
ve Castle Town geçişi istendi. Harita geçişi kabul edildi ancak
60 saniyelik oynanabilir rota penceresi tamamlanmadı.
Sunum iş parçacığında 39 yavaş derleme, 39 farklı tam anahtar ve
toplam 45.647 ms derleme süresi görüldü. En uzun tek derleme
2.425 ms idi. Örneğin program `a1c74226a51fb7ce` için
`dcccfd88bcb9c718` ve `90b41aa253db6947` farklı pipeline'lardır.
Örnek Vulkan sonuçları başarılı ve feedback 0x1 (geçerli,
uygulamanın cache hit biti yok). Swapchain veya FG'nin devrede
olması bu beklemeyi açıklamak için gerekli değildir.

`vk_draw.cpp` içinde `RX_VK_PIPE_SKIP=0`, hazır olmayan tam
pipeline için `wait_for(pe->ready)` çalıştırır. `vk_jobs.cpp`
içindeki `jobs_wait` henüz kuyruktaki işi sunum iş parçacığına
çekebilir. İş bir worker'daysa koşul değişkeninde süre sınırı
olmadan hazır olmasını bekler. Bu durumda tek tek başarılı
derlemelerin seri birikmesi kare sunumunu keser. Timeout eklemek tek
başına yeterli değildir: aynı zaman çizelgesinde çizim/dispatch
atlamak, daha önce eksik geometriye ve beyaz-yeşil yüzeylere eşlik
etti. Dosya tabanlı yerel strict ayarı `ff4bf04` belgelerinde
kayıtlıdır. Repo build veya paket betikleri bu ayarı dağıtım
varsayılanı olarak yazmıyor.

### Son 20 commitin etkisi

| Commit | İncelenen etki |
| --- | --- |
| `7ca5904` | Eksik kareleri FG geçmişinden çıkarır. Strict çizim beklemesini değiştirmez. |
| `1cf178d` | Temple of Time ölçüm raporu. |
| `fe126c1` | Varsayılan cache yazım alanı denetimi. AMD strict cache-only probe opt-in ve koşularda kapalı. |
| `ff4bf04` | Castle Town kaydı ve yerel strict ayarının kullanıma alınması. |
| `19a79e2` | Windows deferred FG acquire 20 ms ve batch kesme. FG Off bu dala girmez. |
| `03c94b5` | Ek audit logları opt-in. GPU timestamp örnek sayacı mevcut toplama yolunda. Backup ve deploy betikleri oyun döngüsü dışında. |
| `86fa8d4` | Installer önizlemesi. |
| `93e7586` | Mako gitlink `bef2014` → `b77ac86`, AMD yamaları rebase. Kontrollü sürüm karşılaştırmasıyla ayrıştırılması gerekiyor. |
| `00ae20c` | Capture araçları ve zaman penceresi. |
| `f76540a` | Vulkan cache yükleme hatası ve cache yokluğu yolları. Cache'in devreden çıkması soğuk derleme sayısını etkileyebilir. |
| `c34ecd1` | Başlangıç cache import için Windows commit bütçesi denetimi. |
| `e2429b5` | Save yükleme geçici çözümünün belgelenmesi. |
| `c2c5386` | Başlangıç preset enumerasyon sonlandırması. |
| `ec41b3c` | FSR GPU süre dağılımındaki geçerli örnekler. |
| `5eb63f1` | FSR input, SDK dispatch ve output GPU ölçümlerinin ayrılması. |
| `9f439f2` | FSR GPU ve oturum ölçümü. |
| `e342bdc` | Kesintiden sonra FSR 3.1 history reset. |
| `4888d22`, `8aae107` | Oyun testi raporları. |
| `98ef846` | Vulkan kabiliyet raporu ve profil önerileri. |

İlk regresyon commit'i kanıtlanmadı. `93e7586` iki upstream
revizyonu karşılaştırmak için sınırdır. `ff4bf04` kod regresyonu
değil, gözlenen beklemeyi tetikleyen yerel konfigürasyonun kaydıdır.

## Bellek, FSR ve sunum

RX 6700M'nin Vulkan device-local heap kapasitesi 10.720.641.024
bayt. Bir Castle Town geçiş örneğinde sürücü yaklaşık 5.928 MiB
usage / 9.426 MiB budget gösterdi. Aynı logda VMA 4.628 MiB block
ve 2.836 MiB aktif allocation gösterdi. WDDM'nin yoğun adaptör
örneğinde 30 ölçümde dedicated en çok 5,40 GiB, shared en çok
1,86 GiB oldu. Bunlar ayrı sayaçlar, farklı kapsam ve zaman
aralıklarına sahipler. Toplanmadılar. Bu ölçümde nihai VMA hatası
yok. Compaction 280 texture taşıyıp 640 MiB blok iade etti.
Compaction maliyetinin tamamı bu ölçümle ayrıştırılamadı.

Bellek yaması mevcut Vulkan bellek türünü ve o türün heap'ini
kullanır. Düşük bütçede spekülatif texture blok tahsisini bekletir.
Render-target blok boyu bütçeye göre seçilir. Yama mevcut
`DEVICE_LOCAL` ve `HOST_VISIBLE` seçimini değiştirmiyor. Bu koşuda
backing tahsis hatası veya yanlış heap seçimi gösterilemedi.
FSR 4.1.2 context oluşumu FFX 0, ilk negatif VkResult yok. FSR
3.1 fallback veya Quality performansı bu koşunun ölçümü değildir.
FG deferred acquire 20 ms korunur. FG Off'ta da görülen spike'lar
gerekçe gösterilerek acquire/fence yoluna müdahale edilmedi.

## Değişiklik ve testler

`patches/pipeline-slow-key.patch` mevcut 300 ms/200 mesaj sınırı
içine tam anahtarı, VkResult ve Vulkan pipeline feedback'i ekler.
`Build-LocalGame.ps1` yamayı uygular. `Measure-FrameTimes.ps1`
P50, maksimum ve 33,3/50/100 ms üstü sayıları ekler.
`Test-MeasureFrameTimes.ps1` gerçek CSV girdisi üzerinden
yüzdelikleri, eşik sınırlarını ve ölçüm penceresini test eder.
Windows x64 Vulkan DLL derlemesi ve oturum yakalama testleri geçti.

FG Off staging CSV'sinde menü ve yükleme dahil 1.957 aralık var.
P50 16,75 ms, P95 30,44 ms, P99 66,81 ms, en uzun 15.514 ms.
61 aralık 33,3 ms, 27 aralık 50 ms, 14 aralık 100 ms üzerinde.
Süreç 112,84 s çalışırken CSV'nin sunum zaman çizelgesi 57,32 s'de
bitti. Son donma tamamlanmış bir aralık olarak sayılmadı. Bu nedenle
istatistikler 60 saniyelik sahne performansı veya A/B kazancı değildir.

Bu değişiklik ölçüm eksiğini düzeltir. Render davranışını koruyan,
pipeline miss'lerini sunumun kritik yolundan çıkaracak kalıcı
düzeltme doğrulanmadı. Altı rota koşusu, gerçek render ve generated
FPS ayrımı, güvenli async miss ve FG/Vulkan yaşam süresine yönelik
yeni davranış testleri tamamlanmadı. Yerel kurulum ve kararlı
Release güncellenmedi. Staging'den geri dönmek için oyunu kapatıp
yerel EXE'yi açın. Kurulu DLL değişirse mevcut doğrulanmış
`Switch-InstalledBuild.ps1 -Restore` yedeği kullanılabilir.

## Tekrarlama

Aynı save ve cache başlangıcıyla Castle Town, Temple of Time ve
Hyrule Field'ı FG Off ve Auto çalıştırın. Aynı çözünürlük, FSR,
VSync ve FPS limitini koruyun. Sahneye girişten sonra 30 s ısınma
ve 60 s ölçüm alın. Derin profiler koşusunu normal koşudan ayrı
tutun. Capture'ın zaman çizelgesi ilk present ile başlar.
Aşağıdaki X değerine sahneye girişten itibaren 30 s eklenmiş CSV
zamanını girin. Son present hedef pencereye ulaşmamışsa koşuyu
başarısız veya eksik kaydedin.

~~~powershell
.\scripts\Capture-VulkanSession.ps1 -GameDirectory $stage -OutputDirectory $out -Scene 'Castle Town'
# İkinci terminalde, capture açıkken
.\scripts\Sample-GpuMemory.ps1 -GameProcessId (Get-Process hookshot).Id -IntervalSeconds 1 -Samples 90 -CsvPath "$out\wddm.csv"
.\scripts\Measure-FrameTimes.ps1 -CsvPath "$out\presents.csv" -SkipSeconds $X -DurationSeconds 60
~~~

Tanılama tekrarında capture'a `-PerformanceAudit` ekleyin ve
`RX_VK_FRAME_TRACE=1` ile `pipe_wait_ms`, `left_out`, tam
pipeline anahtarı, VkResult, FSR provider ve memory loglarını
zamanla eşleştirin. WDDM verisini adaptör örneğine göre ayırın.

### Ön hazırlık ve kısa bekleme denemesi

Yeni manuel oturumun logu, eski `hookshot_prepare_skipped`
işaretinin shader hazırlığını atladığını doğruladı. İşaret yalnızca
staging'de yedeklenerek ön hazırlık açıldı. 38.809 işlik hazırlık
başladı ve bir dakikanın üzerinde hâlâ %0 gösterdi. Tamamlanmadan
kapatıldı ve işaret staging'e geri kondu. Bu koşu, ön hazırlığın
rota performansına etkisini doğrulamadı.

Ardından aynı staging'de FG Off, FSR 4.1.2 Native AA ve yalnızca
atlamasına izin verilen çizimlerde kare başına 4 ms bekleme denendi
(`RX_VK_PIPE_SKIP=1`, `RX_VK_PIPE_WAIT_MS=4`, probe ve quick
kapalı). FSR 4.1.2 dispatch'i devam etti. Hyrule Field'da oyun
ilerledi, Castle Town komutu geçişi tamamlamadı ve son durumda
2696. karede 0 FPS/stalled raporlandı. Frame trace 2.681 satırda
11.941 bekleyen iş atlaması ve tek satırda 1.163 atlama gösterdi.
Ekran görüntüsü isteği zaman aşımına uğradı. Bu deneme sıkı koşuyla
eş bir rota ölçümü veya görsel doğrulama değildir. 4 ms yalnız
atlamasına izin verilen işe uygulanır; gerekli işler hâlâ
bekleyebilir. Deney ayarları yalnızca test sürecinin ortamındaydı.
Kurulu sürüme veya dağıtım varsayılanlarına uygulanmadı.
