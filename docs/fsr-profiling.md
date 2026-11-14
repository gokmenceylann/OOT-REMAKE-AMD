# FSR 4 GPU profiling

Use `scripts/Capture-VulkanSession.ps1 -GameDirectory <test-game> -OutputDirectory <new-directory> -PassTiming`. It invokes the existing game EXE and collects logs and present intervals when available. Use an isolated game directory. Analyze fixed scene windows with `Measure-FrameTimes.ps1`.

The Vulkan profiler reports three GPU spans: `FSR 4 Mako inputs` (including actor motion), `FSR 4 SDK dispatch`, and `FSR 4 Mako output`. It converts Vulkan timestamp ticks using the device's timestamp period. These spans include GPU dependencies inside their boundaries. They are separate from CPU actor-motion and replay timings and do not represent full end-to-end frame latency. Use unprofiled runs for throughput comparisons because global pass timing changes replay scheduling.

The Windows x64 build linked successfully. The temporal history suite passed 7,647 checks, and resource retirement and synthetic frametime tests passed. On RX 6700M the isolated capture enabled the profiler and read 47,797 shader program keys. Startup logged an nn.npln worker mutex wait and no present CSV or FSR dispatch was recorded before the run was closed. The mutex warning alone does not establish the startup cause.

No matched 60-second scene runs, new FSR GPU timings, FFX=3 reproduction, visual attribution or memory-policy measurements resulted from this run. The original install was retained. See [existing observations](fsr-stability-report.md).

## Profiler doğrulama takibi

Profiler örneği bir command-buffer aralığıdır. Aynı kayıt yuvasının tamamlanması sonrası sorgular okunur; sonuçlar tek tek sunum kareleriyle eşleştirilmez. Üç FSR 4 aralığı ardışık tutulur; aralarındaki bariyer ve layout geçişlerinin tamamı bu üç süreye dahil değildir. Sorgu süresi timestampPeriod ile GPU milisaniyesine çevrilir. Queue timestampValidBits desteklenmiyorsa profiler başlatılmaz. Geçersiz veya okunamayan sorgular için sıfır örnek üretilmez.

Her rapor penceresinde FSR 4 aralıkları için geçerli örnek sayısı, ortalama, medyan, P95, P99 ve maksimum ayrı yazılır. Bu dağılımlar dispatch başınadır. FSR 3.1'in mevcut pass raporu farklı kapsamda olduğundan karşılaştırma sırasında hazırlık ve çıktı maliyetleri ayrıca ele alınmalıdır.

5eb63f1 ayrı doğrulama dizininde incelendi. Profiler kapalı ve doldurulmuş pipeline cache ile yapılan kontrol de shader anahtarlarını okudu ve oyun sahnesine ulaşmadan sonlandırıldı. Aynı nn.npln uyarısı geçmişte AV1 açılışını ve kare sunumunu başarıyla geçen bir oturumda da mevcut. Profiler overhead, üç modun eşlenmiş benchmark'ı, Castle Town pass maliyetleri ve kamera artefaktı bu çalışmada ölçülemedi. Context retirement ve temporal history politikası bu değişiklikte düzenlenmedi.
