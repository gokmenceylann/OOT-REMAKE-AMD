# Known issues and support

The current maintenance line tracks Windows x64 and the Mako commit pinned in the repository. RX 6700M behavior is documented in the [validation notes](validation-rx6700m.md) and [memory telemetry report](memory-telemetry.md). Performance varies by scene and settings.

- An AMD FSR 4.1.2 Native AA resolution change previously returned SDK error 3 at context creation. The recovery patch adds diagnostics and a bounded retry. The exact underlying Vulkan error and in-game reproduction with the patched renderer are open. [Recovery details](fsr-context-recovery.md)
- Presentation tearing and temporal artifacts can look similar. FIFO with frame generation disabled provides a controlled comparison. The cause of the observed camera-turn artifact is unconfirmed.
- A Vulkan memory budget display near 100% is dynamic process telemetry. Compare WDDM dedicated/shared and VMA separately.
- The tools release requires local game generation. The open-source tools installer contains no game data or bundled AMD driver/SDK.

Report reproducible issues using the repository bug form. Include the current commit or release tag and Mako revision.
