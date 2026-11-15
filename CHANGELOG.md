# Changelog

## v0.1.6

- Verified rebuilt Mako 4.1.1 Vulkan renderer with the original Windows x64 game EXE.
- Added exact-runtime local import installer and portable package with optional locally supplied AMD FSR Vulkan DLL pair.
- Added Windows worker failure and Vulkan import rollback regression gates.

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
