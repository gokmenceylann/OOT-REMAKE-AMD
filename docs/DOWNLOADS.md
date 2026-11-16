# Downloads and local game files

| Release | Windows x64 setup | Portable | Verification |
| --- | --- | --- | --- |
| **v0.1.6 stable** | [Setup](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/download/v0.1.6/OOT-REMAKE-AMD-v0.1.6-game-import-setup.exe) | [ZIP](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/download/v0.1.6/OOT-REMAKE-AMD-v0.1.6-game-import.zip) | [SHA-256](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/download/v0.1.6/SHA256SUMS.txt) |
| **v0.2.0-rc.4 experimental diagnostics** | [Setup](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/download/v0.2.0-rc.4/OOT-REMAKE-AMD-v0.2.0-rc.4-game-import-setup.exe) | [ZIP](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/download/v0.2.0-rc.4/OOT-REMAKE-AMD-v0.2.0-rc.4-game-import.zip) | [SHA-256](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/download/v0.2.0-rc.4/SHA256SUMS.txt) |

These are local importers. Supply your own `image.bin`, `romfs` and exact local `hookshot.exe` / `hookshot_vk.dll` pair. Setup compares the pair against a release manifest and installs to a separate directory. Start `hookshot.exe` directly. The packages contain import tooling and documentation. Game files, game runtime binaries and AMD SDK binaries are supplied separately.

For a new local build, follow [the source build guide](BUILDING.md) and launch the output directly. Rebuilt binaries can differ from the release manifest. For AMD FSR 4.1.2, supply the official Vulkan loader/upscaler pair. See [installation](install.md) and [known issues](KNOWN_ISSUES.md) before choosing the diagnostic build.

Follow the instructions for the release you downloaded. [v0.1.6 stable installation](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.1.6/docs/stable-v0.1.6.md) · [v0.2.0-rc.4 experimental installation](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.2.0-rc.4/docs/install-v0.2.0-rc.4.md)
