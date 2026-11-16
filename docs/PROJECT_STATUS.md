# Project status

| Track | Scope | Evidence |
| --- | --- | --- |
| [v0.1.6](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/tag/v0.1.6) | Current stable local importer | Exact runtime hashes and RX 6700M smoke validation |
| [v0.2.0-rc.4](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/tag/v0.2.0-rc.4) | Prerelease local importer and texture diagnostics | Windows x64 renderer build, FSR dispatch and test route samples |
| [performance/stable-mako-411](https://github.com/gokmenceylann/OOT-REMAKE-AMD/tree/performance/stable-mako-411) | Cache, memory and replay diagnostics | Opt-in measurements and targeted regression tests |

On 16 November 2026 the diagnostics branch was `0fbfe44d074c119b9887da18c28d4487e49be1db`, and the default branch started at `d7782905437d4502865e721546da8b9bdf51fa67`. Both pin Mako `b77ac86187330eb7447ac65ab23187baac4600ca`. The default branch contains earlier experiments recorded in the project history. Those reports do not establish behavior in rc.4.

**Verified on the tested configuration.** Vulkan startup, save loading, region transitions and real FSR 4.1.2 dispatch. **Experimental.** Texture profiling and pipeline/cache diagnostics. **Open.** Memory pressure, transition-time missing draws, controlled performance comparisons and wider GPU validation.

[Known issues](KNOWN_ISSUES.md) · [Hardware matrix](GPU_COMPATIBILITY.md) · [rc.4 measurement report](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.2.0-rc.4/docs/mako-411-memory-owner-and-texture-profile.md)
