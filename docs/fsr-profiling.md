# FSR 4 GPU profiling

Use `scripts/Capture-VulkanSession.ps1 -GameDirectory <test-game> -OutputDirectory <new-directory> -PassTiming`. It invokes the existing game EXE and collects logs and present intervals when available. Use an isolated game directory. Analyze fixed scene windows with `Measure-FrameTimes.ps1`.

The Vulkan profiler reports three GPU spans: `FSR 4 Mako inputs` (including actor motion), `FSR 4 SDK dispatch`, and `FSR 4 Mako output`. It converts Vulkan timestamp ticks using the device's timestamp period. These spans include GPU dependencies inside their boundaries. They are separate from CPU actor-motion and replay timings and do not represent full end-to-end frame latency. Use unprofiled runs for throughput comparisons because global pass timing changes replay scheduling.

The Windows x64 build linked successfully. The temporal history suite passed 7,647 checks, and resource retirement and synthetic frametime tests passed. On RX 6700M the isolated capture enabled the profiler and read 47,797 shader program keys. Startup logged an nn.npln worker mutex wait and no present CSV or FSR dispatch was recorded before the run was closed. The mutex warning alone does not establish the startup cause.

No matched 60-second scene runs, new FSR GPU timings, FFX=3 reproduction, visual attribution or memory-policy measurements resulted from this run. The original install was retained. See [existing observations](fsr-stability-report.md).

## Profiler doğrulama takibi

Profiler örneği bir command-buffer aralığıdır. Aynı kayıt yuvasının tamamlanması sonrası sorgular okunur; sonuçlar tek tek sunum kareleriyle eşleştirilmez. Üç FSR 4 aralığı ardışık tutulur; aralarındaki bariyer ve layout geçişlerinin tamamı bu üç süreye dahil değildir. Sorgu süresi timestampPeriod ile GPU milisaniyesine çevrilir. Queue timestampValidBits desteklenmiyorsa profiler başlatılmaz. Geçersiz veya okunamayan sorgular için sıfır örnek üretilmez.

Her rapor penceresinde FSR 4 aralıkları için geçerli örnek sayısı, ortalama, medyan, P95, P99 ve maksimum ayrı yazılır. Bu dağılımlar dispatch başınadır. FSR 3.1'in mevcut pass raporu farklı kapsamda olduğundan karşılaştırma sırasında hazırlık ve çıktı maliyetleri ayrıca ele alınmalıdır.

5eb63f1 ayrı doğrulama dizininde incelendi. Profiler kapalı ve doldurulmuş pipeline cache ile yapılan kontrol de shader anahtarlarını okudu ve oyun sahnesine ulaşmadan sonlandırıldı. Aynı nn.npln uyarısı geçmişte AV1 açılışını ve kare sunumunu başarıyla geçen bir oturumda da mevcut. Profiler overhead, üç modun eşlenmiş benchmark'ı, Castle Town pass maliyetleri ve kamera artefaktı bu çalışmada ölçülemedi. Context retirement ve temporal history politikası bu değişiklikte düzenlenmedi.

## Castle Town and Hyrule Field

Use a separate session directory under `D:\codex` for each run. The collector writes
`session.json` on exit, including the executable, PID, exit status, log size,
last message and elapsed time. Timestamps in the stderr log record receipt on
the host. A newly written native log can be recovered when stderr is empty.
Recovery keeps native messages as written. A failed launch, empty log or
missing frame samples prevents creation of a success summary.

Warm each route before measuring. Use the same save, camera path, settings,
render/output resolution and cache state. Turn Frame Generation off and keep
V-Sync and the FPS limit identical. Start one process per provider and one
separate process for Game scaler. Record Castle Town and Hyrule Field as
distinct 60-second windows. The CSV clock begins at the first present.
Use `-SkipSeconds` and `-DurationSeconds 60` for the chosen interval and record
its bounds. Compare unprofiled runs first, then repeat with `-PassTiming` to
inspect GPU spans and estimate the overhead of profiling.

Record the actual dispatch provider from the renderer log. Retain dispatch
dimensions and distinguish Native AA from upscaling. Present intervals
measure presented frames. Compare them with the GPU span and replay timings,
and keep Vulkan heap usage/budget, VMA block/allocation sizes and Windows
dedicated/shared readings in separate columns. Periodic GPU and memory lines
can span a wider interval than the selected frame CSV window.

For visual reproduction record the scene and elapsed video time. Repeat the
Castle Town entry with Game scaler, FSR 3.1 and FSR 4.1.2. Collect a separate
validation run with `RX_VK_VALIDATION=1` if the Khronos validation layer is
installed. Validation timing is unsuitable for throughput comparison. The
current logs cannot correlate every resource transition or FSR dispatch with
an individual present, and the absence of validation output does not rule out
a rendering artifact.

### Recorded evidence

A mixed v0.1.3 session recorded CPU replay submission windows at 22.56–28.81 ms,
including 5.80–6.81 ms of memory sync in those two windows. Present calls
were 0.30–0.47 ms. A device heap snapshot reported 8012 of 8266 MiB used,
6451 MiB in VMA blocks and 5136 MiB allocated by VMA. The same session
reported a compaction moving 335 textures and returning 768 MiB in blocks.
These observations establish memory pressure and substantial replay work
during that session. The capture has no matched route or per-frame
correlation to identify which stage limited Castle Town or Hyrule Field.

A video showed green-white surfaces and broken geometry near 00:50 on
entry to Castle Town. The next run's sampled frames did not show it. There
is no matching validation or resource trace for that frame, so the visual
cause remains open.

The new capture tools recorded 1176 stderr lines and 2325 present intervals
during an RX 6700M startup and menu smoke run. No Castle Town or Hyrule Field
performance result is derived from that run. The previous zero-byte log had
no process or exit metadata, so its historical cause cannot be established.
