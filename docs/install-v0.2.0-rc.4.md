# v0.2.0-rc.4 — Mako 4.1.1 tanılama test kurulumu

Windows 11 x64, Vulkan sürücüsü ve SHA-256 değerleri doğrulanan yerel Mako oyun dosyaları gerekir. Setup, test edilen oyun EXE/DLL çiftini yerel kaynaktan ayrı hedef klasöre aktarır. Bu bir Release Candidate'tır. Kararlı sürüm v0.1.6'dır.

1. Setup EXE veya portable ZIP dosyasını SHA256SUMS.txt ile doğrula.
2. Kurulumda test edilmiş eşleşen hookshot.exe ve hookshot_vk.dll, kendi image.bin ve romfs dizininin bulunduğu yerel derleme klasörünü seç. Manifest STABLE-RUNTIME-SHA256.txt dosyasında. Farklı DLL'ler preflight sırasında reddedilir.
3. Yeni bir hedef dizin seç ve hedefte doğrudan hookshot.exe aç. Yükseltmeden önce kaynak klasörünü ve kişisel kaydını koru. Kurucu mevcut kurulumun üzerine yazmayı engeller.
4. FSR için AMD'nin resmi loader ve upscaler Vulkan DLL'lerinin ikisini yerel kaynak klasörüne yerleştir. Setup ikisini birlikte aktarır. Windows 11 N'de Media Feature Pack gerekebilir.

Portable paket içinde scripts/Import-LocalGame.ps1 komutuna -GameDirectory ve -Destination ver. -CheckOnly ile önce preflight çalıştırılabilir. Oyun EXE/DLL'leri, Nintendo oyun dosyaları ve AMD runtime ikilileri GitHub varlıklarına dahil değildir. Bu paket boş bir sistemdeki ilk yerel derleme için gerekli kaynak dosyalarını sağlamaz.

Tanılama için RX_VK_TEXTURE_PROFILE=1, image view, doku hazırlığı, sampler ve hazard örneklerini renderer loguna ekler. Ortam değişkeni ayarlanmadığında profil kapalı. [Ölçüm raporu](mako-411-memory-owner-and-texture-profile.md)
