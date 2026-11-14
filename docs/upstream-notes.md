# Açık kaynak referansları

- [mkw-recomp](https://github.com/adriadam10/mkw-recomp/blob/main/README.md): AArch64 lift ve SDK işlevlerine isimle karşılık verme. NVN2 nesnelerini ve komut kaydını Vulkan yürütümünden ayıran bir tasarım kullanıyor.
- [libnx](https://github.com/switchbrew/libnx/blob/master/nx/include/switch/kernel/svc.h): Horizon SVC imzaları ve veri yapıları için referans.
- [N64Recomp](https://github.com/N64Recomp/N64Recomp/blob/main/src/recompilation.cpp): Statik çağrı ve dolaylı hedef çözümlemesi için referans. İşlemci mimarisi farklıdır.

İlk rtld çağrısının bellek doldurma davranışı yerel oyun modülü üzerinde test edildi. Oyun kodu veya bu projelerden kaynak kod buraya kopyalanmadı.

```powershell
python -m pip install -r requirements-dev.txt
python probe_rtld_fill.py 'C:\Games\OOT\exefs\rtld' --entry 0x21e0
```

Unicorn yalnızca diferansiyel testte referans olarak çalışır. Test ayrı bir misafir sayfasındaki baytları ve X0 dönüşünü Python host uygulamasıyla kıyaslar. Henüz native giriş programına bağlanmış bir çağrı veya oyun çalıştırma desteği yoktur. Ofset yalnızca doğrulanan oyun derlemesine aittir.
