# OOT-REMAKE-AMD | Ocarina of Time PC recomp

An open-source Windows x64 project for locally building and testing a Zelda: Ocarina of Time PC port with Mako 4.1.1, Vulkan and AMD FidelityFX Super Resolution. The project maintains renderer patches, reproducible build instructions and hardware test reports. Run the locally built `hookshot.exe` directly.

[Stable v0.1.6](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/tag/v0.1.6) · [Diagnostics v0.2.0-rc.4](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/tag/v0.2.0-rc.4) · [Build from source](docs/BUILDING.md) · [Türkçe](README.tr.md)

## Project scope and upstream

[Mako 4.1.1 at `b77ac861`](https://github.com/Shakoquo/Mako/tree/b77ac86187330eb7447ac65ab23187baac4600ca) supplies Hookshot-derived AArch64 static recompilation, the Horizon host runtime and the NVN2-to-Vulkan renderer. This repository pins that source and layers AMD Vulkan compatibility and diagnostics on top. The [architecture guide](docs/ARCHITECTURE.md) maps the upstream code, project patches and build output.

The repository welcomes Vulkan compatibility reports from AMD, NVIDIA and Intel users. Published hardware verification is currently limited to the Radeon RX 6700M configuration in the [GPU matrix](docs/GPU_COMPATIBILITY.md).

## What works and what is under investigation

| Area | Current evidence |
| --- | --- |
| Windows x64 Vulkan | The RX 6700M ran the direct executable, loaded a save and completed tested region transitions. |
| FSR 4 integration | Logs recorded actual FSR 4.1.2 Vulkan dispatch on the RX 6700M with the matching AMD runtime. The renderer retains the FSR 3.1 fallback. |
| AMD Vulkan optimization | Project patches cover Vulkan memory allocation and budget diagnostics, cache import safeguards and FSR context handling. |
| Experimental profiling | The rc.4 branch offers opt-in texture replay timing. The test build still showed memory pressure and some draws with pending pipelines. |
| Frame generation and wider GPU coverage | Hardware compatibility and image stability remain unverified across devices. Published comparison runs used FG Off. |

See [project status](docs/PROJECT_STATUS.md), [known issues](docs/KNOWN_ISSUES.md) and [test conditions](docs/TESTING.md). The project has no verified general FPS target.

## Install or build

- **Platform.** Windows 11 x64 and a Vulkan-capable GPU driver. The documented test PC had a Ryzen 7 5800H, Radeon RX 6700M and 32 GB RAM. The tested hardware is a reference configuration.
- **Release setup.** The Windows setup and portable ZIP import an existing, matching local build. The downloads contain documentation and import tools. Supply the exact EXE/DLL pair and your own game data; setup checks the runtime manifest. [Installation guide](docs/install.md)
- **Source build.** Supply compatible locally extracted ExeFS and RomFS, initialize the Mako submodule, and run the Windows build script with Python, LLVM MinGW and the pinned headers. Start the resulting `game/hookshot.exe`. [Commands and dependencies](docs/BUILDING.md)
- **FSR runtime.** Obtain the official AMD Vulkan loader and upscaler pair for FSR 4.1.2. The test log identifies the provider actually dispatched. [FSR configuration and logs](docs/fsr-4.1.2.md)

## Contribute and report problems

Use [CONTRIBUTING.md](CONTRIBUTING.md) to choose a branch, validate your changes and open a pull request. Use the [issue forms](https://github.com/gokmenceylann/OOT-REMAKE-AMD/issues/new/choose) for bugs, GPU tests, performance measurements or visual artifacts. Include your exact build and driver. Share focused logs and numerical summaries with personal information removed.

## License and related projects

See [GPLv3 license text](LICENSE), [third-party notices](THIRD-PARTY.md) and [source provenance](docs/ARCHITECTURE.md). [Mako](https://github.com/Shakoquo/Mako), [Hookshot](https://git.magicbean.dev/MagicBeanDev/Hookshot) and [AMD GPUOpen FSR](https://gpuopen.com/amd-fsr-sdk/) document the corresponding upstream work. Nintendo game content, keys and game-derived binaries remain local to the user.
