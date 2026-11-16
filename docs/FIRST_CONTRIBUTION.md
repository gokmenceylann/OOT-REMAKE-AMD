# Your first contribution

1. Fork the project and read [project status](PROJECT_STATUS.md) to choose an area.
2. Check [architecture](ARCHITECTURE.md) and [upstream provenance](UPSTREAM-PROVENANCE.md). Read [CONTRIBUTING.md](../CONTRIBUTING.md) before choosing a branch.
3. For code changes, set up the toolchain and build from [the Windows guide](BUILDING.md). Keep input game data outside the checkout.
4. Test on your GPU using the [test procedure](TESTING.md). A report can be useful even if a test fails or cannot be completed.
5. Share the exact configuration via the [GPU report form chooser](https://github.com/gokmenceylann/OOT-REMAKE-AMD/issues/new/choose). Open a small pull request with the changed files, test commands and results.

| Area | Starter contribution |
| --- | --- |
| Documentation | Reproduce a build instruction or fix a stale link. |
| Build system | Report a reproducible missing dependency or clarify setup. |
| Vulkan renderer | Isolate a rendering problem and identify the first relevant log. |
| GPU compatibility | Submit one driver and build combination with accurate coverage. |
| Performance profiling | Reproduce a route with consistent graphics and cache state. |
| Testing | Check a previously untested save/load or transition scenario. |
| Bug fixes | Reproduce one failure and include a regression check where practical. |
