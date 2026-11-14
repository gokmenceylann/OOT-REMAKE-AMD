# Troubleshooting / Sorun giderme

| Symptom / Belirti | Check / Kontrol |
| --- | --- |
| Game does not open / Oyun açılmıyor | Run the preflight script and verify the local build output and matching RomFS. / Ön kontrolü çalıştır ve eşleşen RomFS’yi doğrula. |
| Vulkan DLL missing / Vulkan DLL eksik | Verify `hookshot_vk.dll` is beside the EXE and install the GPU vendor’s Vulkan driver if the system loader is missing. |
| FSR 4.1 unavailable or falls back | Check the two AMD DLLs, selected GPU, successful dispatch and context errors in the [FSR guide](fsr-4.1.2.md). |
| White overlay, ghosting or tearing / Beyaz kaplama, iz veya yırtılma | Compare Game, FSR 3.1 and FSR 4 with V-Sync On and Frame Generation Off. Record the scene and whether the problem survives with the Game scaler. |
| Shader cache stall / Shader takılması | Allow first-use compilation to finish. Back up existing caches before testing a fresh folder. |
| VRAM full / Bellek dolu | Record a driver budget snapshot and WDDM memory. [Telemetry guide](memory-telemetry.md) |
| Save does not load / Kayıt yüklenmiyor | Close the game, confirm the active user directory, preserve a copy of the save, and verify the title/version matches. |
| Performance drop / FPS düşüşü | Reproduce in the same scene with the same cap, render resolution and frame generation settings. Include frametimes and provider logs. |

Game logs are beside the direct EXE as `hookshot_log.txt` and rotated variants when file logging is available. The local builder writes `<LocalRoot>\build.log`. Include the release or commit, GPU, driver, Windows build, scaling mode, and relevant log lines. Remove personal paths and keep game files and saves private.

## Kayıt yüklenirken oyun kapanıyor

Logda buffer veya komut tamponu tahsis hatası görülürse, PowerShell'de oyun dizinine geçip aşağıdaki komutla bir oturum dene. Örnek yolu kendi oyun klasörünle değiştir.

```powershell
Set-Location 'D:\OOT-local\game'
$previous = $env:RX_VK_PCACHE_LOAD
try {
    $env:RX_VK_PCACHE_LOAD = '0'
    Start-Process -FilePath '.\hookshot.exe' -WorkingDirectory (Get-Location).Path
} finally {
    $env:RX_VK_PCACHE_LOAD = $previous
}
```

Bu ayar ana Vulkan pipeline cache dosyasının bu oturumda belleğe yüklenmesini atlar. Mevcut shader program cache'i okunabilir ve cache dosyalarını silmek gerekmez. Bazı pipeline'lar oyun sırasında yeniden derlenebilir. RX 6700M testinde sorun çıkaran kayıt açıldı ve oyun içinde FSR 4.1.2 dispatch'i loglandı. Normal EXE açılışında varsayılan davranış geçerlidir.

**English:** For save-load exits with allocation failures in the log, use the PowerShell example above to skip loading the main Vulkan pipeline cache for one run. The separate shader program cache can still load. This workaround was verified on RX 6700M with a successful save load and FSR 4.1.2 dispatch.

## Otomatik pipeline cache bellek kontrolü

Windows renderer, ana Vulkan pipeline cache'i okumadan önce süreç için kullanılabilir sistem commit alanını sorgular. İçe aktarmanın geçici maliyeti için dosya boyutunun iki katını, sahne yüklemesi için de 4 GiB pay ayıran bir eşik kullanır. Bu eşik bir bellek tahminidir. Vulkan device-local bütçesi, VMA tahsisleri ve WDDM dedicated/shared sayaçları ayrı kalır.

Yer kalmazsa veya ana cache içe aktarılamazsa renderer boş bir Vulkan pipeline cache ile devam eder ve ana cache dosyasını değiştirmez. Shader program cache'i ayrı okunur. Oyun sırasında pipeline derlemesi görülebilir. Logda atlanan dosya boyutu ve mevcut commit alanı veya Vulkan içe aktarma hatası bulunur.
