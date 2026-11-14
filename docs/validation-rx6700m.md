# İlk Windows ölçümü

Mako 4.1 kaynak revizyonu bef2014, MSI Delta 15 A5EFK ve PresentMon 2.6.0. Windows x64 derlemesi 34 dakika 43 saniyede tamamlandı. Doğrudan EXE çalıştırıldı, Mako penceresi yanıt verdi, oyun işlemi Vulkan DLL'ini ve AMD Vulkan sürücüsünü yükledi ve 3D GPU etkinliği gösterdi.

Başlatma profili 1920×1080, doğal işleme, Vulkan, 60 FPS sınırı ve Frame Generation kapalı olarak istendi. İlk açılışta 60 saniyede 1.727 PresentMon aralığı ölçüldü. Ortalama 28,82 FPS, P95 35,331 ms ve P99 35,623 ms. Sahne ve fiziksel GPU seçimi görsel olarak doğrulanmadı. Bu ölçüm önceki Hookshot kaydıyla kontrollü bir A/B testi değildir. FSR ve uzun süreli oyun kararlılığı doğrulanmadı.

İlk açılış iki uygulanmamış SDK importu bildirdi. Süreç çalışmaya devam etti. Çeviriden ve oyun verisinden üretilen dosyalar yerelde kaldı.

[İlk kayıtlı FSR 4.1.2 Native AA oyun içi testi](fsr-first-test-rx6700m.md)

[FSR 4 Quality, Frame Generation Off ve V-Sync On — Castle Town testi](fsr-quality-test-rx6700m.md)
