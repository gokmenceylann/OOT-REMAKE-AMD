# GPU compatibility

| Vendor and model | Renderer | Driver and OS | FSR evidence | Status |
| --- | --- | --- | --- | --- |
| AMD Radeon RX 6700M | Vulkan | AMD proprietary 26.10.1, Windows 11 x64 | FSR 4.1.2 dispatch recorded on 16 November 2026 at 1920×1080 Native AA and 1440×810 → 1920×1080; FG Off | Verified for documented scenarios |
| Other AMD models | Vulkan | — | — | Untested in published matrix |
| NVIDIA | Vulkan | — | — | Untested in published matrix |
| Intel | Vulkan | — | — | Untested in published matrix |

The RX 6700M result covers the diagnostic build and tested save/route. It does not establish 30 or 60 FPS stability, frame generation support, or support across driver versions. Report your dedicated GPU capacity separately from Vulkan budget and WDDM shared memory.

Submit the GPU model and driver from the renderer log, Windows edition and build, CPU/RAM, build SHA, render/output resolution, selected and dispatched FSR version, frame generation and V-Sync state, and which tests passed or failed. [Report GPU compatibility](https://github.com/gokmenceylann/OOT-REMAKE-AMD/issues/new/choose) · [RX 6700M validation](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.2.0-rc.4/docs/mako-411-memory-owner-and-texture-profile.md)
