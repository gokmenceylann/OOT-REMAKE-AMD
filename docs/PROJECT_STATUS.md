# Project status

| Track | Scope | Evidence |
| --- | --- | --- |
| [v0.1.6](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/tag/v0.1.6) | Current stable local importer | Exact runtime hashes and RX 6700M smoke validation |
| [v0.2.0-rc.4](https://github.com/gokmenceylann/OOT-REMAKE-AMD/releases/tag/v0.2.0-rc.4) | Prerelease local importer and texture diagnostics | Windows x64 renderer build, FSR dispatch and test route samples |
| [performance/stable-mako-411](https://github.com/gokmenceylann/OOT-REMAKE-AMD/tree/performance/stable-mako-411) | Cache, memory and replay diagnostics | Opt-in measurements and targeted regression tests |

The stable release was built from `66aa0e1` and the diagnostics prerelease from `0fbfe44`. Both pin Mako `b77ac86187330eb7447ac65ab23187baac4600ca`. Use the release tag and the reported configuration when comparing test results.

**Verified on the tested configuration.** Vulkan startup, save loading, region transitions and real FSR 4.1.2 dispatch. **Experimental.** Texture profiling and pipeline/cache diagnostics. **Open.** Memory pressure, transition-time missing draws, controlled performance comparisons and wider GPU validation.

[Known issues](KNOWN_ISSUES.md) · [Hardware matrix](GPU_COMPATIBILITY.md) · [rc.4 measurement report](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.2.0-rc.4/docs/mako-411-memory-owner-and-texture-profile.md)
