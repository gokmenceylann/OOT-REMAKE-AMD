# GPU compatibility

**Verified** means the stated scenario ran on the listed configuration. **Partial** means some checks passed with gaps. **Failed** means the test found a problem. **Untested** indicates no published verification.

| Vendor / model | Driver and OS | Build and date | Vulkan | Coverage |
| --- | --- | --- | --- | --- |
| AMD Radeon RX 6700M | AMD proprietary 26.10.1, Windows 11 x64 (build number unrecorded) | rc.4, `0fbfe44`, 16 November 2026 | Verified for startup and save load | Partial overall |
| Other AMD models | — | — | Untested | Untested |
| NVIDIA | — | — | Untested | Untested |
| Intel | — | — | Untested | Untested |

### RX 6700M scenario details

| Check | Result |
| --- | --- |
| FSR provider / dispatch | Verified FSR 4.1.2 Vulkan, FG Off, at 1920×1080 Native AA and 1440×810 to 1920×1080. |
| Save and regions | Save load verified. Native AA completed two Field/Market loops. Scaled FSR reached Castle Town before the window closed. |
| Visual coverage | Partial. A sampled image had no white/green overlay. Pending draws were logged and complete transition coverage is open. |
| Frame times | Native AA second entry 60 s, 17.34 raw presents/s, 6.05 1% low and 130.30 ms P99. Scaled first entry 10 s, 16.63 raw presents/s, 2.85 1% low and 299.78 ms P99. Scene histories differed. |
| Long run and common performance target | Untested for the full 15-minute acceptance run and controlled comparison. |

Record the GPU vendor and model, driver, OS build, CPU and RAM, SHA and date, render and output size, renderer, FSR mode/provider, FG, scene, startup and save, region transitions and image artifacts. Add game FPS and present FPS separately, 1% low, P95/P99 and dedicated capacity versus Vulkan budget or WDDM use. Use the status for the precise scenario. [GPU issue chooser](https://github.com/gokmenceylann/OOT-REMAKE-AMD/issues/new/choose) · [Recorded test](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.2.0-rc.4/docs/mako-411-memory-owner-and-texture-profile.md)
