# Known issues

The reports preserve the observed symptoms and test conditions. A fix for the Castle Town frame-time spikes, Windows commit pressure or missing draws during transitions has yet to be validated. Share reproductions, findings and measured patches in the [open findings issue](https://github.com/gokmenceylann/OOT-REMAKE-AMD/issues/5).

| Issue | Current evidence |
| --- | --- |
| Windows system commit pressure | rc.4 observed high private commit and small system headroom. VMMap classified part of the growth as host-side anonymous private memory. The allocation owner remains unresolved. |
| Missing draws during area changes | Logs record pending pipelines during transitions. A single clean screenshot cannot validate the whole transition. |
| Castle Town frame pacing | Native AA and scaled runs used differing scene histories. The reports do not establish a controlled performance improvement or a sustained 30/60 FPS result. |
| FSR context and provider differences | Use provider and context logs to distinguish a real 4.1.2 dispatch from another path. Other devices and drivers require verification. |
| Release installation | Setup requires the matching local EXE/DLL and legal game data. Choose a separate destination and use a real source folder if Windows blocks a junction. |
| Coverage | Sustained 15-minute acceptance, repeatable multi-run A/B and GPU vendor coverage remain open. |

[Diagnostics report](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.2.0-rc.4/docs/mako-411-memory-owner-and-texture-profile.md) · [Troubleshooting](troubleshooting.md) · [Earlier known issues](known-issues-history.md)
