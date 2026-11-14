# RX 6700M — İlk kayıtlı FSR 4.1.2 oyun içi testi

14 Kasım 2026. Windows x64, RX 6700M, Vulkan. Siyah ekran sonrası önceki renderer DLL'ine dönülen yerel kurulum kullanıldı.

| Kontrol | Sonuç |
| --- | --- |
| Sağlayıcı | Başarılı FSR 4.1.2 dispatch, provider ID 17700776140664213506. |
| Mod | Native AA, çoğunlukla 1536×864 → 1536×864. Log art arda 600 işlenen kare bildirdi. |
| Context geçişi | 1536×864 → 1429×804 → 1536×864. Eski context'ler FFX=0 ile imha edildi ve yenileri başarılı dispatch yaptı. |
| Fallback | Bu oturumda 3.1 fallback veya 4.1 dispatch hatası kaydedilmedi. Önceki 1152×648 → 1536×864 hata senaryosu tekrarlanmadı. |
| Sunum | 1280×720 swapchain, dört görüntü, IMMEDIATE, V-Sync Off. |
| Performans | Kaydın sonuna yakın beş saniyelik oyun logu pencerelerinde 15,4–32,1 FPS. Kontrollü benchmark yapılmadı ve sabit 60 FPS doğrulanmadı. |

OBS kaydı yaklaşık 34 saniye, 1280×720 ve 30 FPS. Videoda oyun içi sahne ile AMD FSR 4 seçimi görüldü. Monitör yırtılması ile temporal artefakt kayıttan kesin ayrıştırılamadı.

Log kanıtı:

    FSR provider dispatched: 4.1.2 (id=17700776140664213506) on AMD Radeon RX 6700M, 1536x864 -> 1536x864
    AMD FSR 4: context 1536x864 made frame 2647 destroyed frame 3395 (FFX=0)
    FSR provider dispatched: 4.1.2 (id=17700776140664213506) on AMD Radeon RX 6700M, 1429x804 -> 1429x804
    AMD FSR 4: context 1429x804 made frame 3395 destroyed frame 3397 (FFX=0)
    FSR provider dispatched: 4.1.2 (id=17700776140664213506) on AMD Radeon RX 6700M, 1536x864 -> 1536x864

Quality modu ve eşit çözünürlükte FSR 3.1 kıyaslaması açık. [Kontrollü karşılaştırma planı](amd-compatibility.md)
