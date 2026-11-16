# Architecture and source provenance

| Layer | Source and responsibility |
| --- | --- |
| Static recompilation | Pinned Mako `nx2/` translates the user's local AArch64 input and builds the Windows x64 executable. |
| Game runtime | Mako `host/` implements Horizon-compatible host services. Local game data is supplied separately. |
| Rendering | Mako `gpu/vk/` records Vulkan work and ships a separate `hookshot_vk.dll` that the executable loads. |
| Compatibility patches | Project patches cover FSR context and history handling, Vulkan allocation telemetry and Radeon memory policy. The diagnostics branch also carries queue, cache budget and replay instrumentation patches. |
| Tooling | PowerShell handles local build/import and capture. Inno Setup packages the local importer. |

The gitlink pins [Mako 4.1.1 `b77ac86187330eb7447ac65ab23187baac4600ca`](https://github.com/Shakoquo/Mako/tree/b77ac86187330eb7447ac65ab23187baac4600ca). Hookshot and Mako supply the underlying engine. The published diagnostic baseline records Longshot as a source reference. See the [pinned provenance](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.2.0-rc.4/docs/UPSTREAM-PROVENANCE.md) and [component inventory](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.2.0-rc.4/docs/THIRD-PARTY-COMPONENTS.md).

FSR 4.1.2 uses the official Vulkan SDK interface when a compatible provider initializes. The log records the dispatched version. The built-in FSR 3.1 route is the fallback. See [FSR integration](fsr-4.1.2.md) and [Vulkan memory](vulkan-memory.md).
