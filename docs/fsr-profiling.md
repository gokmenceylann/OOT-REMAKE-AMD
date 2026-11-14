# FSR 4 GPU dispatch profiling

`scripts/Capture-VulkanSession.ps1` launches the existing local game EXE and captures stderr and Vulkan present intervals. Use a separate capture directory for each mode. The full-session summary includes boot and menus. Use `Measure-FrameTimes.ps1` with a fixed start and duration for a scene comparison.

For GPU measurements pass `-PassTiming`. The renderer reports an `FSR 4 SDK dispatch` timestamp span. It covers commands recorded by the SDK and excludes Mako's input preparation and final output pass. A separate unprofiled run is needed for throughput because global pass timing changes replay scheduling. FSR 3.1 already reports per-pass timings.

The patched Windows x64 renderer compiled and linked. Temporal history passed 7,647 checks. An RX 6700M startup in a separate validation directory enabled the profiler and read 47,797 shader program keys. That run did not reach a measured scene. The original game EXE and renderer were retained. No new Castle Town FPS, SDK timing, fallback reproduction or visual comparison was measured. See [previous observations](fsr-stability-report.md).
