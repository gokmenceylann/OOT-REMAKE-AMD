# Contributing

Start with [project status](docs/PROJECT_STATUS.md), [architecture](docs/ARCHITECTURE.md) and the [Windows build guide](docs/BUILDING.md).

1. Fork the repository. Base documentation and packaging changes on `main`. Base rc.4 diagnostics or renderer work on `performance/stable-mako-411` and open the pull request against that branch. Include the starting SHA.
2. Initialize the pinned Mako submodule in a clean checkout. Put local builds and game data outside Git. Keep upstream-derived changes in small patches and note the source commit and license.
3. Use one behavior change per commit. Include a short rationale, the test command and its result, plus any remaining hardware validation.
4. Run the [documentation and build checks](docs/TESTING.md). For Vulkan changes, provide a renderer build and use the same save, camera route, resolution, frame generation state and cache conditions for game comparisons.
5. Open a pull request using the checklist. Include before/after evidence, risks and any source licensing changes.

For hardware and bug reports, use the [issue chooser](https://github.com/gokmenceylann/OOT-REMAKE-AMD/issues/new/choose). Record the GPU model, exact driver, Windows build, renderer/provider, settings, test date and outcome. Use [GPU compatibility](docs/GPU_COMPATIBILITY.md) and [known issues](docs/KNOWN_ISSUES.md) to label what you actually observed. Keep Nintendo files, keys, saves, caches, SDK DLLs and full memory snapshots local.
