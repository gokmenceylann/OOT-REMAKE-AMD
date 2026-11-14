# RX 6700M — FSR 4 Quality, Hyrule Castle Town

14 Kasım 2026, 23:02. Yaklaşık 52 saniyelik OBS kaydı, 1280×720 ve 30 FPS. Aşağıdaki değerler videodaki oyun içi sayaçlardan alınan örneklerdir.

| Ayar | Videodaki değer |
| --- | --- |
| GPU | AMD Radeon RX 6700M |
| Upscaler | AMD FSR 4, Quality %67 |
| İç render çözünürlüğü | 1024×576 |
| Menüdeki çıkış çözünürlüğü ayarı | 1920×1080 |
| Frame Generation / V-Sync | Off / On |
| Frame pacing / oyun FPS sınırı | On / 60 FPS |

| Gözlem | Videodaki değer |
| --- | --- |
| Menü | Yaklaşık 60 FPS |
| Hyrule Castle Town, örneklenen oyun içi kareler | Yaklaşık 15–33 FPS |
| Son bölümde görülen kare süresi | Yaklaşık 30–49 ms |
| Son bölümde görülen %1 düşük FPS | 9–13 FPS |

Castle Town sahnesinde 60 FPS hedefi sağlanmadı. Bu örneklerden oturum ortalaması veya P95/P99 çıkarılmadı. Oyun logu boş olduğundan bu oturumun gerçek FSR 4.1.2 dispatch'i, fallback durumu ve fiilî Vulkan present mode'u doğrulanamadı. Video menüdeki seçimi doğruluyor.

Önceki [Native AA testi](fsr-first-test-rx6700m.md) farklı V-Sync ve Frame Generation koşullarıyla kaydedildi. Quality ile Native AA arasındaki performans farkını ölçmek için eşlenmiş sahne ve ayarlar gerekiyor. [Karşılaştırma planı](amd-compatibility.md)
