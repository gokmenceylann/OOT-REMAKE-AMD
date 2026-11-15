# Changelog

## v0.1.6

- Released the verified Mako 4.1.1 EXE and rebuilt Vulkan renderer as a local import workflow.
- Added Windows setup and portable packages with exact runtime hashes and optional locally supplied AMD FSR Vulkan DLLs.
- [Source, installation and verification](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.1.6/docs/stable-v0.1.6.md)

## v0.2.0-rc.3

- Packaged a new Windows baseline importer for the verified v0.1.5 local runtime.
- Added Mako and Longshot source provenance and RX 6700M gameplay measurements.
- Updated the bilingual project overview. Runtime binaries are shared with the v0.1.5 baseline.

## v0.1.5

- Updated the pinned Mako source to 4.1.1 and rebased the Vulkan patches.
- The capture tool recognizes Mako 4.1.1's native log location.

## v0.1.4

- Added Vulkan session status, timestamped stderr, stale log rejection and scene-window summaries.
- Added capture tools and a repeatable Castle Town and Hyrule Field test procedure to the tools release.

## Unreleased

- Added bilingual installation instructions, preflight checks and support templates.
- Added portable tools packaging, optional Inno Setup packaging and SHA-256 manifests.
- Added replay-timeline FSR context retirement, bounded retries and camera history resets.
- Known gaps: exact FSR runtime error and controlled visual comparison remain unverified. See [known issues](docs/known-issues.md).
