# Vulkan ve Windows bellek telemetrisi

`-EnableMemoryOptimization` ile derlenen renderer, mevcut 600-present örnekleme noktasında VMA bayt ve nesne sayaçlarını yazdırır. Başarısız VMA istekleri önceki oran sınırlı günlükte yer alır. Windows süreci için ayrı örnekleme:

```powershell
.\scripts\Sample-GpuMemory.ps1 -GameProcessId 1234 -IntervalSeconds 5 -Samples 12 -CsvPath 'D:\gpu-memory.csv'
```

WDDM GPU Process Memory CIM sayacı her bağdaştırıcı LUID ve fiziksel düğüm için dedicated kullanım, shared kullanım ve total committed değerlerini doğrudan okur. Total committed, dedicated ve shared değerlerini elle toplayarak elde edilmez. Local/nonlocal da ayrı WDDM ölçüleridir. Telemetri için DXGI QueryVideoMemoryInfo uygulanmadı. Bu sayaçlar Vulkan kullanımına veya VMA toplamına eklenmez.

Vulkan heap size aygıtın bildirdiği heap kapasitesidir. Budget sürücünün dinamik süreç bütçesidir, usage ise sürücü tahminidir. VMA block bytes ayrılmış blokların boyutunu, allocation bytes o bloklardaki ve dedicated ayırmalardaki aktif allocation boyutunu gösterir. Alt sayaçlar VMA toplamının parçalarıdır. Sampled etiketi özel texture havuzunu, render-target hedef olarak sınıflandırılan görüntüleri, depth depth/stencil attachment'ları gösterir. Other-image genel görüntüleri de içerir. FSR geçici görüntüleri other-image/buffer içinde yer alabilir. SDK iç belleği ve temporal görüntüler için renderer'ın mevcut upscaler durum satırını kullan; bunları VMA toplamına yeniden ekleme. Driver pipeline ve swapchain kaynakları alt sayaçların dışında kalabilir.

## Cache ve tahliye

- `vk_texture.cpp` adres/format/şekil tabanlı texture cache ve render-target havuzu kullanır. Tam eşleşen hedefler görünüm nesneleriyle yeniden kullanılabilir. Eski hedefler 120 present sonrası, 256 MiB havuz sınırı aşılırsa veya VRAM baskısında budanır.
- Texture LRU bütçesi sürücü baskısına göre daralır. Kullanılmayan adaylar yaş ve yeniden oluşturulabilirlik koşullarıyla seçilir. GPU tarafından yazılmış texture'lar gerekirse staging'e toplu geri yazılır ve fence beklenir. Bazı içerikler güvenle geri yazılamadığından tutulur. Bu politika değiştirilmedi.
- ASTC dönüştürme ve upload staging'i ile tahliye writeback beklemeleri maliyet oluşturabilir. Mevcut günlükler yükleme baytları, yeniden kullanılan hedefler, tahliyeler ve tekrar yüklemeler hakkında özet verir. Farklı guest adreslerindeki eşit içerik genel olarak tekilleştirilmez.
- AMD üzerinde spekülatif texture bloğu önden hazırlama, seçilen heap'te iki bloktan az bütçe boşluğu varsa bekler. Gerçek talepler eski allocation yollarını kullanır. `RX_VK_BLOCK_AHEAD_LOW_BUDGET=1` önceki önden ayırma davranışını geri getirir.
- Önceki 64 MiB hedef havuzu deneyi aynı 128 MiB rezervasyon ve örnek anında 64 MiB daha yüksek toplam kullanım gösterdi. Bu veri kazanç kanıtı değildir. Hedef havuzu için önceki seçici ve override korunur.

## Yerel doğrulama

Windows x64 incremental Vulkan derlemesi 0 hatayla tamamlandı. RX 6700M test sürecinde Vulkan device-local heap kapasitesi 10.720.641.024 bayt, sürücünün anlık bütçesi 9.426 MiB olarak raporlandı. Kapasite cihazın API bilgisidir; bu değer ile Windows toplam committed veya shared kullanım karıştırılmamalıdır. Bir WDDM örneğinde aynı GPU düğümü 1.266.384.896 dedicated, 410.116.096 shared ve 1.640.849.408 committed bayt bildirdi. Aynı örnekleme penceresinden alınmadıkları için bu değerler Vulkan ile doğrudan fark hesabında kullanılmadı.

Hyrule Castle kontrollü karşılaştırması, düşük bütçe altında önden ayırma eşiğinin tetiklenmesi ve görüntü kalitesi bu ölçümle doğrulanmadı. FPS iyileşmesi iddia edilmiyor.
