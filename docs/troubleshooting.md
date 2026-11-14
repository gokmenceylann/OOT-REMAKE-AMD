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
