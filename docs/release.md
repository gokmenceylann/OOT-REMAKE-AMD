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

The `game-import-preview` job runs only when someone starts the workflow
manually with `workflow_dispatch`. On pull requests, the `package` job
compiles the v0.1.6 and v0.2.0-rc.4 game import installers and checks the
ZIP contents and SHA-256 manifests without publishing them.

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

## Published exact-runtime importers

[v0.1.6](DOWNLOADS.md) is the stable importer. v0.2.0-rc.4 is the experimental diagnostics importer. Each package verifies the local EXE and Vulkan DLL against its own SHA-256 manifest. Downloads contain the importer and documentation. Supply the matching local binaries and your own game data.

The packaging script selects the version's manifest automatically when you
pass `-GameImport` with either published version. For example, to build and
check the stable installer in a separate directory, run:

```powershell
$version = 'v0.1.6'
$compiler = 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe'
$out = "D:\OOT-import-$version"
.\scripts\New-ReleasePackage.ps1 -Version $version -OutputDirectory $out -InnoCompiler $compiler -GameImport
.\scripts\Test-ReleasePackage.ps1 -PackageDirectory $out -ExpectedRuntimeManifest "installer/$version-runtime-sha256.txt"
```

Set `$version` to `v0.2.0-rc.4` to check the diagnostics importer. The
manifest hashes come from the respective release source commits. A locally
rebuilt pair may have different hashes and can be launched directly from its
output folder.
