# Releases

Use `vMAJOR.MINOR.PATCH` tags. Increment PATCH for compatible fixes, MINOR for compatible features and MAJOR for changes requiring a user migration.

A tag starts the Windows tools workflow. It creates a tools ZIP, an Inno installer and `SHA256SUMS.txt`. It verifies packaging and installation before publishing a draft GitHub Release. Review and publish the draft from GitHub. The workflow takes only a fixed allowlist of repository files. Game data and locally lifted executables stay on the user's PC. The local builder creates the game independently of packaging.

To create the ZIP locally, initialize the Mako submodule and run:

```powershell
.\scripts\New-ReleasePackage.ps1 -Version v1.0.0 -OutputDirectory D:\OOT-release
```

Pass `-InnoCompiler 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe'` for the optional tools installer. The installer does not register a game shortcut because the user generates the game in a separate location. It provides Start Menu and optional desktop links to the instructions. When testing the installer, use a clean directory.

Check a download with `Get-FileHash -Algorithm SHA256 -LiteralPath <file>` and compare the result with the matching entry in `SHA256SUMS.txt`. Checksums verify integrity against the published manifest.

Before tagging, update [CHANGELOG.md](../CHANGELOG.md). Review the [release template](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/main/.github/release-template.md) and record Windows, GPU, renderer, tested dependencies, and unverified conditions.

## Windows game import preview

Build the approval candidate by adding `-GameImport` and an Inno compiler
path to the packaging command. Keep the generated installer, ZIP and SHA-256
manifest in a separate test directory. Confirm the import, direct EXE launch,
missing dependencies, real Vulkan and FSR behavior, and uninstall preservation
in a Windows 11 test environment before approving a stable release.

Inno Setup fits the writable game directory and external file selection. The
setup copies files supplied locally and can create a direct EXE shortcut.
An MSIX deployment would add signing and package identity requirements while
the game stores cache alongside the executable. The preview has its own app
identity. Publishing a stable release and updating an existing local game
are separate approval steps.
