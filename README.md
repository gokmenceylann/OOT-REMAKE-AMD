# OOT-REMAKE-AMD

[Download Latest Release](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/latest) · [Installation Guide](docs/install.md) · [Known Issues](docs/known-issues.md) · [Build from Source](docs/mako-build.md) · [Türkçe](README.tr.md)

A Windows x64 project for running a locally built native Ocarina of Time port. It uses a pinned Mako revision for Hookshot-style AArch64 static recompilation, Horizon host services and NVN2-to-Vulkan rendering. Run the resulting `hookshot.exe` directly.

## What you can download

Release assets contain setup documentation and a Windows preflight tool. The portable ZIP and optional tools installer contain no game executable. The pinned build links translated game code into its EXE and generates an image from game data. Use your own compatible extracted ExeFS and RomFS with the local builder to produce both. If the latest-release page has no release, follow the source installation guide.

## Requirements and features

- Windows 11 x64 and a Vulkan-capable GPU driver. Development validation used an AMD Radeon RX 6700M, Ryzen 7 5800H and 32 GB RAM. Other GPU and driver combinations are unverified unless documented.
- A compatible local ExeFS/RomFS pair, Git, Python and the pinned build dependencies described in the [build guide](docs/mako-build.md).
- Vulkan renderer, optional Radeon memory patch and [Vulkan/WDDM telemetry](docs/memory-telemetry.md).
- Optional AMD FSR Upscaling 4.1.2 with the official Vulkan SDK runtime and built-in FSR 3.1 fallback. Upscaling and frame generation are separate. [FSR setup](docs/fsr-4.1.2.md)
- [Known issues](docs/known-issues.md), [troubleshooting](docs/troubleshooting.md), and [hardware validation](docs/validation-rx6700m.md).

## FAQ

**Can I run a game directly from the release ZIP?** Generate the EXE and image on your PC using the [installation guide](docs/install.md).

**Where are saves and graphics options?** For the default direct EXE layout, back up `game/user/save/` and `game/hookshot_options.ini`. Keep shader and pipeline caches in the same game folder when updating.

**Why does FSR 4.1 switch to 3.1?** Inspect the actual provider dispatch and context errors in the log. [FSR diagnostics](docs/fsr-context-recovery.md)

## Project and licensing

[Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Release process](docs/release.md) · [GPLv3 license text](LICENSE) · [Third-party notices](THIRD-PARTY.md)

This is an independent project. Nintendo game content, keys, game-derived executables and generated game assets are kept local. Use files you are entitled to use. Preserve upstream and SDK license notices.
