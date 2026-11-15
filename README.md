# OOT-REMAKE-AMD

Windows 11 x64 project for a locally built Ocarina of Time recompilation. It uses Mako 4.1.1 and its Hookshot/Longshot ancestry for AArch64 static recompilation, Horizon host services and NVN2-to-Vulkan rendering. The game starts directly from `hookshot.exe`.

[Stable v0.1.6](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/tag/v0.1.6) · [Research preview](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/tag/v0.2.0-rc.3) · [Türkçe](README.tr.md)

## Choose a release

| Release | Use |
| --- | --- |
| **v0.1.6 stable** | Import the verified local Mako 4.1.1 installation with its rebuilt Vulkan DLL. This is the default GitHub release. |
| **v0.1.5 original baseline** | Restore the first verified Mako 4.1.1 EXE/DLL pair. |
| **v0.2.0-rc.3 research preview** | New Windows importer package for the same verified runtime, with source provenance and an RX 6700M baseline report. |
| **v0.2.0-rc.1 / rc.2** | Older previews. rc.2 has documented Castle Town stutter and geometry issues. |

The Windows x64 setup and portable ZIP are **local import tools**. Supply the matching `hookshot.exe`, `hookshot_vk.dll`, `image.bin` and `romfs` from your own compatible local build. The baseline importer verifies the exact game EXE and Vulkan DLL hashes. If you have a different valid source build, use the general source-build instructions. Game binaries, Nintendo content, keys, game-derived shader caches and AMD SDK DLLs stay local. Verify downloads with the release SHA-256 manifest.

## Setup and runtime

1. Use Windows 11 x64 and a Vulkan-capable graphics driver.
2. For a source build, supply your own compatible extracted ExeFS/RomFS and the pinned toolchain in the [build guide](docs/mako-build.md).
3. For a verified baseline import, use the installer or portable package and select a separate game destination. Run `hookshot.exe` from that directory.
4. Back up `user/save/` and `hookshot_options.ini`. Keep compatible shader and pipeline caches when updating.

[Installation](docs/install.md) · [Release and checksum guide](docs/release.md) · [Troubleshooting](docs/troubleshooting.md)

## Tested on RX 6700M

The baseline test used an RX 6700M, Ryzen 7 5800H, 32 GB RAM and Vulkan. With FG Off, it completed Castle Town → Hyrule Field → Castle Town and dispatched the **FSR 4.1.2 Native AA** provider at 1536×864. The partial post-warmup window covered 56.2 seconds and averaged **16.59 presents/s**, with **147.79 ms P99**. The separate game counter averaged about **12.79 FPS**. This is a baseline measurement with unresolved performance issues. FSR 3.1 fallback is available. Frame generation is a separate path.

[Baseline test](docs/mako-411-baseline-validation.md) · [FSR setup](docs/fsr-4.1.2.md) · [Vulkan and WDDM telemetry](docs/memory-telemetry.md) · [Known issues](docs/known-issues.md) · [Stutter investigation](docs/stutter-root-cause-report.md)

## Source and licensing

The verified baseline is OOT `93e7586` with Mako `b77ac861`. The research preview documents which Longshot work was already inherited by Mako. It bundles no new Longshot code or runtime. This is an independent project. Upstream GPL and third-party notices apply as documented.

[Source provenance](docs/recomp-source-provenance.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [License](LICENSE) · [Third-party notices](THIRD-PARTY.md)
