# Testing

## Automated checks

Run `python -I -B scripts/check_docs.py` from the repository root after staging new files. The Documentation workflow checks the required community files and local Markdown links on pull requests. Windows Vulkan renderer CI compiles the pinned renderer and the release workflow verifies package structure. The diagnostics branch has additional renderer fixtures. These automated jobs use synthetic or build-only checks. Hardware results are recorded separately.

## Hardware checks

1. Record the project commit, binary hashes, Windows build, GPU and exact driver. Use an isolated copy of the save and options.
2. Launch `hookshot.exe`, load the same save and follow a fixed Hyrule Field and Castle Town route. Capture a frame on entry and after warmup, and log the actual FSR provider, render/output resolution, FG, V-Sync and limiter.
3. For comparisons, keep camera input, timing, cache state and profiling settings fixed. Repeat each case and label cold and warm runs.
4. Record the actual game frame counter, presented FPS, 1% low, P95/P99, CPU replay, GPU timestamps and failures. Keep Vulkan heap budget, VMA allocation and WDDM dedicated/shared counters separate.
5. Close and relaunch. Record whether the save still opens, whether any textures or geometry are missing, and how long the session lasted.

Use [capture tools](fsr-profiling.md), [memory telemetry](memory-telemetry.md) and the [published test conditions](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.2.0-rc.4/docs/mako-411-memory-owner-and-texture-profile.md).
