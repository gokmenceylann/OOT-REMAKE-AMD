# FSR 4.1 context recovery

The Windows Vulkan renderer retires the old FSR upscale context and its resized input/output images on the existing replay completion timeline. It preserves the game's upscale while waiting for GPU completion. A surviving FSR context is reused for render-size changes that do not change its output. A context-creation runtime error schedules one new attempt after 60 texture frames. If that attempt fails, the existing FSR 3.1 fallback applies.

Set `RX_VK_FSR4_DEBUG=1` for one run to enable AMD SDK debug checking and per-call Vulkan resource logs. The context attempt and completion records are keyed by renderer frame. They include resolution, selected provider, SDK flags, device-local usage/budget, VMA heap statistics, and the first negative result returned by a wrapped Vulkan call. Only synchronous calls exposed through the SDK's provided device proc table are observable. A summary with zero observed calls or no failing operation leaves the underlying SDK error unresolved. Vulkan does not expose the byte cost of driver pipeline or descriptor objects through the create calls.

The FSR 4 camera history reset uses jitter-corrected reprojection. It resets on a large loss of prior viewport overlap near the middle and farther into the frustum. Smaller pans retain history. The frame's motion preparation and the SDK's reset flag use the same decision. This heuristic can miss cuts between overlapping views.

For a visual comparison, use the same save point and camera movement with Frame Generation Off and V-Sync On. Compare Game, FSR 3.1, and FSR 4 at matching render/output resolution. Verify the active provider from dispatch logs. Keep Native AA resolution-transition reproduction separate from that comparison.
