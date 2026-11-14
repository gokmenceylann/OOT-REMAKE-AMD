# RX 6700M Vulkan memory audit

## Allocation paths

| Resource | Mako source and lifetime |
| --- | --- |
| Sampled guest textures | `gpu/vk/vk_texture.cpp` caches decoded images. VMA uses the general image pool or a separate texture pool with compaction. ASTC conversion can allocate staging and scratch resources. |
| Render targets and depth | Guest attachments share the texture cache and can use a separate device-local VMA pool. Dynamic resolution changes target sizes. Live allocations and reserved block bytes are different measurements. |
| Upscaler | `vk_temporal.cpp` reuses color, depth, motion and output images at the same allocated dimensions and defers replaced images. `vk_fsr4.cpp` reuses one exposure texel and one SDK context for the same output extent. The SDK owns its internal allocations. |
| Shader and pipeline state | `vk_shader.cpp` and `vk_replay.cpp` manage shader and pipeline caches. Disk cache sizes are not VRAM. Driver-owned pipelines and swapchain memory can contribute to heap usage outside VMA. |
| Temporary buffers | `vk_vma.cpp` chooses mapped host memory for staging/captures where requested and device-local memory for GPU buffers. Guest memory imports and replay mirrors are tracked separately in the renderer. |

VMA enables driver budgets when VK_EXT_memory_budget is available. The general allocator prefers 64 MiB blocks. Image pools default to 128 MiB blocks. Image allocation tries device-local memory within budget, then retries without the flag, then can fall back to system memory.

## Observed pressure and boundaries

- A longer prior run logged a render-target pool with 640 MiB reserved and 201 MiB live. This gap includes reusable free ranges. It does not prove the ranges can be released while live images pin their blocks.
- Texture allocation and upload can produce synchronous work. `vk_vma.cpp` already preallocates texture blocks off-thread. `vk_texture.cpp` batches writebacks before evicting GPU-written images and waits for completion. Upload and ASTC conversion share staging and scratch storage with explicit barriers. Removing those waits or aliasing the images requires a separate dependency analysis.
- The FSR SDK context and temporal buffers already persist across frames. Their allocation and retirement policies stay intact. No quality, synchronization or Vulkan feature settings are changed.

## Opt-in patch

Pass `-EnableMemoryOptimization` to the existing build script. With the patch, discrete AMD devices use 64 MiB render-target blocks when the selected heap reports a nonzero budget of at most 9 GiB. Other pools keep their upstream policies. `RX_VK_TARGET_BLOCK_MB=128` restores the upstream target block size for a run. `RX_VK_TARGET_BLOCK_MB=64` forces the smaller size. The target override takes precedence over the existing general image block override. For a clean upstream build, start from a fresh checkout and omit the switch. Applied patches remain in the local submodule checkout.

Final image/buffer failures log VkResult, resource class, dimensions/format for images, requested bytes for buffers, and per-heap budget/usage/reserved/live bytes. Logs are rate-limited. The patch preserves existing fallback paths.

## Local Windows x64 validation

The Vulkan renderer rebuilt and linked with FSR support, with zero failed compiles in the incremental build. The existing EXE loaded the renderer from a separate validation folder. The installed game, saves and shader cache were left in place.

| Run | Present FPS | P95 | P99 | Target pool reserved / live |
| --- | ---: | ---: | ---: | ---: |
| Baseline, 60 s | 60.00 | 17.856 ms | 18.746 ms | 128 / 64 MiB |
| Patched, automatic, 60 s | 60.00 | 17.638 ms | 18.513 ms | 128 / 64 MiB |
| Patched, forced 64, 30 s | 60.00 | 17.623 ms | 18.738 ms | 128 / 64 MiB |

The driver reported a 9426 MiB aggregate budget in these samples. Forced 64 used two blocks instead of one, with equal reserved bytes and 64 MiB more reported total usage in its sampled snapshot. These runs therefore do not demonstrate lower VRAM use or faster frame pacing. The scene was not visually verified, and no successful FSR dispatch or allocation failure was observed during these captures. Full game rebuild, allocation failure injection, long gameplay and high-pressure A/B measurements remain unverified.
