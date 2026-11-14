# Radeon compatibility and 60 FPS validation

The renderer reports Vulkan vendor/device IDs, API and driver versions, enabled memory-budget support, mesh path, buffer device addresses and shader capabilities. Device names are descriptive. The mesh workarounds still use the existing Vulkan capability checks with device-ID exceptions for known driver failures.

| Family | Renderer path | Upscaling checks | Hardware coverage |
| --- | --- | --- | --- |
| RX 5000 / RDNA 1 | Compute mesh path when native mesh is absent and BDA is available | 4.1.2 requires AMD SDK enumeration and verified dispatch. 3.1 requires compatible storage formats and push descriptors. | Unverified |
| RX 6000 / RDNA 2 | Native mesh or the existing task-mesh compute workaround | Same checks. RX 6700M previously dispatched AMD 4.1.2 and built-in 3.1. | RX 6700M only |
| RX 7000 / RDNA 3 | Uses exposed Vulkan capabilities | Same checks | Unverified |
| RX 9000 / RDNA 4 | Uses exposed Vulkan capabilities | Same checks | Unverified |
| GCN / unknown | Requires Vulkan renderer baseline. Without both native mesh and compute fallback, rendering can be incomplete. | Same checks. Game scaler remains available if upscalers cannot run. | Unverified |

The device must expose dynamic rendering, synchronization2 and timeline semaphores. The Graphics quality preset help gives a recommendation from discrete device-local heap capacity and process budget. Integrated/unknown devices see Minimum. These are starting points; selecting a preset applies it. Existing saved settings stay in place until changed by the player. The first-run upstream policy stays in place. The renderer does not use a model name to infer architecture, mobility or SDK support.

For a baseline, use a 60 FPS game cap, Frame Generation Off, V-Sync On and FSR 4 Quality if a successful 4.1.2 dispatch is logged. Try Balanced and FSR 3.1 at matching render scale, and use Native AA as a full-resolution comparison. Keep the same save, camera path, output resolution and shader-cache state. For Castle and an ordinary area, capture three 60-second runs after warm-up. Run a second throughput series without a 60 cap if settings exceed it. Keep the series separate.

Set `RX_VK_FRAME_LOG` to a new absolute CSV path before launching. The CSV records present intervals. Use `scripts/Measure-FrameTimes.ps1 -CsvPath <path> -SkipSeconds 30 -DurationSeconds 60` to summarize average FPS, slowest-tail 1% and 0.1% FPS and nearest-rank P95/P99. Tail estimates require at least two samples in the selected tail. Record Vulkan present mode, real/generated frames, GPU utilization, CPU utilization, and dedicated/shared counters alongside the frame log. Use [memory telemetry](memory-telemetry.md) for VMA and Vulkan budgets. Track replay GPU waits, pipeline compilation, texture compaction and uploads in the same time window before attributing Castle spikes.

Previous user reports of 20–50 FPS with FSR 4.1 Quality and 60–100 with FSR 3.1 in Castle were not controlled equal-resolution measurements. The open diagnostics include FSR context transitions under memory pressure, temporal artifacts and the relative cost of actor motion and GPU passes.

[AMD FSR SDK 2.4](https://gpuopen.com/learn/amd-fsr-sdk-2-4-rx-6000-ryzen-apus/)
