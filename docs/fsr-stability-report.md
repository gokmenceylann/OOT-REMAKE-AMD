# FSR kararlılık takibi — RX 6700M

## Bulgular

- 805cb67 yerelde mevcut. Bu commit'in FSR yaması 249827b ile aynı. Sonraki main sürümleri context retirement, SDK tanılama ve tek retry davranışını içeriyor.
- Önceki hatalı Native AA geçişinde FFX=3 ve ardından fallback kaydedildi. Alttaki VkResult kaydedilmedi. Texture compaction aynı zaman aralığındaydı. Bu gözlemler bellek hatasını ispatlamaz. Sonraki 1536×864 → 1429×804 → 1536×864 geçişi başarılı oldu. [Native AA kaydı](fsr-first-test-rx6700m.md)
- Native AA oturumunun geç bölümünde renderer 17,0–25,1 ms GPU süresi/kare, bazı pencerelerde 47–48 ms en uzun GPU submission ve yaklaşık 2.140–2.516 draw/kare raporladı. 25,1 ms, 60 FPS için 16,67 ms bütçesini aşıyor. Aynı aralıkta texture compaction bir işlemde 778 texture taşıdı. Sayaçlar GPU maliyetini ve kaynak hareketini gösterir, tek başına hangi pass'in veya hangi sahne olayının gecikmeyi ürettiğini göstermez.
- Castle Town Quality videosunda 15–33 FPS gözlendi. O oturumun logu boş olduğu için Native AA sayaçlarıyla eşleştirilemiyor. Hyrule Castle ayrı bir sahne olarak ölçülmeli. [Quality kaydı](fsr-quality-test-rx6700m.md)

## Değişiklik ve doğrulama

FSR 3.1 kamera girdileri, upscale kaydedilemese de ilerleyebiliyor. Son başarılı dispatch'in kare numarası artık output kaydından sonra güncelleniyor. İlk dispatch, kare boşluğu veya aynı karede tekrar dispatch history reset alıyor. FSR 4.1 context recovery ve kamera kesmesi kodu korunuyor. Bu değişikliğin gözlenen görsel bozulmayı giderdiği henüz doğrulanmadı.

Windows x64 Vulkan renderer 25 saniyede 0 hatayla derlendi. Temporal history testi 7.647 kontrolde 0 hata verdi. FSR 3.1 ve frame interpolation kaynak emekliliği testleri geçti. Mevcut oyun EXE'si yerinde bırakıldı. Yeni DLL ile sahne A/B testi ve önceki FFX=3 geçişi tekrar edilmedi.

## Karşılaştırma

Aynı kayıttan, aynı kamera yolu ve ısınmış cache ile ayrı 60 saniyelik Native AA, FSR 3.1 Quality ve FSR 4 Quality yakalamaları al. Frame Generation Off, V-Sync ve iç/çıkış çözünürlüğünü kaydet. Native AA tam çözünürlüklü referanstır; iki Quality koşusunun iç çözünürlüğünü ayrıca eşleştir.

Her koşu için RX_VK_FRAME_LOG CSV'sini ve stderr logunu ayrı kaydet. Measure-FrameTimes.ps1 ile ortalama, düşük dilimler ve P95/P99 hesaplanabilir. Sample-GpuMemory.ps1 ile aynı zaman aralığında WDDM dedicated/shared değerlerini al. GPU/CPU ayrımı için renderer replay, GPU süreleri ve PresentMon verisini eşleştir. FSR provider dispatch, context hatası, fallback ve texture compaction satırlarını rapora ekle. Önceki FFX=3 geçişinde RX_VK_FSR4_DEBUG=1 ile varsa gözlemlenebilir Vulkan hatasını yakala. [Ayrıntılı ölçüm planı](amd-compatibility.md)
