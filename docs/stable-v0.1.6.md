# v0.1.6 — Windows x64 kararlı yerel kurulum

## Bu sürümün tabanı

Mako 4.1.1 ve OOT v0.1.5'in kaynak tabanı korunur.
Windows x64 Vulkan renderer `mako-4.1.1-longshot` dalında
kararlı FSR ve Radeon yamalarıyla yeniden derlendi.
İlgili renderer CI commit'i `4f28810`. Pipeline worker hata
ve Vulkan import rollback testleri geçti.

Bu sürüm, kullanıcı tarafından yerelde çalıştığı doğrulanan
eşleşmiş EXE/DLL çiftini referans alır. Paket yeni bir oyun
ikilisi veya performans yaması içermez. Orijinal v0.1.5 EXE'si
aynı kaldı ve Vulkan DLL'i yeniden derlendi. Save, shader/cache
ve ayarlar mevcut yerel kurulumda korundu.

## Kurulum / Installation

1. Windows 11 x64 ve Vulkan sürücüsü kullanın. Windows 11 N için
   Media Foundation bileşeni gerekebilir.
2. Windows setup veya portable ZIP'i indirip `SHA256SUMS.txt`
   ile doğrulayın.
3. Kurulumda bu sürümün eşleşen `hookshot.exe` ve
   `hookshot_vk.dll` dosyalarını, `image.bin` ve dolu `romfs`
   dizinini içeren kendi yerel klasörünüzü seçin.
4. Ayrı bir hedefe kurun ve hedefteki `hookshot.exe` dosyasını
   açın. Kurulum ve kaldırma, save ve ayarları korur.
5. AMD FSR Vulkan loader ve upscaler DLL'lerinin ikisi de
   kaynak klasörde varsa v0.1.6 içe aktarma aracı ikisini
   yerelden kopyalar. SDK dosyaları indirmeye gömülü değildir.
   FSR için AMD'nin resmi SDK dağıtımını kullanın.

Portable ZIP için içinden
`scripts/Import-LocalGame.ps1 -GameDirectory <yerel-klasör>
-Destination <yeni-klasör>` çalıştırın. Her iki paket runtime
SHA-256 sözleşmesini `STABLE-RUNTIME-SHA256.txt` içinde taşır.
Farklı derlemeler SHA-256 doğrulamasında reddedilir.
Oyun dökümü, üretilmiş oyun EXE'si, renderer DLL'i, cache ve
AMD SDK DLL'leri GitHub indirmesine dahil değildir.

The Windows x64 installer performs a complete **local import**
of the verified build. A matching source folder must already exist.
The installer uses the original EXE with the refreshed Vulkan DLL.
Neither the installer nor the portable archive contains game data
or the runtime files supplied by the user.

## Doğrulama

- [Windows Vulkan CI](https://github.com/gokmenceylann/OOT-REMAKE-AMD/actions/runs/43751820439)
- RX 6700M üzerinde başlangıç kareleri ve normal kapanış
  doğrulandı. Kullanıcı bu kurulu sürümün çalıştığını bildirdi.
- Bu sürüm için yeni FPS karşılaştırması, tam bölge matrisi
  veya ikinci bilgisayarda gerçek oyun doğrulaması yapılmadı.
- [Upstream ve kaynak kökeni](UPSTREAM-PROVENANCE.md)
- [Üçüncü taraf bileşenleri](THIRD-PARTY-COMPONENTS.md)
