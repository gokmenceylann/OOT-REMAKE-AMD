# Upstream provenance

`upstream/mako` pins [Mako 4.1.1](https://github.com/Shakoquo/Mako/tree/b77ac86187330eb7447ac65ab23187baac4600ca) at `b77ac86187330eb7447ac65ab23187baac4600ca`. Mako supplies the Hookshot-derived recomp, host runtime and Vulkan renderer. The [archived Hookshot source](https://git.magicbean.dev/MagicBeanDev/Hookshot) documents that upstream project.

OOT-REMAKE-AMD maintains patches and Windows build tooling around this pin. The [rc.4 provenance record](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.2.0-rc.4/docs/UPSTREAM-PROVENANCE.md) documents Longshot as a reference and identifies ancestry and reviewed revisions. It records no new Longshot binary intake for the diagnostic release.

The project carries the [GPLv3 license text](../LICENSE). Source and patch notices retain upstream licensing. Vendored dependencies retain their individual terms. The AMD runtime pair is supplied separately by the user. See [third-party notices](../THIRD-PARTY.md) and the [pinned component inventory](https://github.com/gokmenceylann/OOT-REMAKE-AMD/blob/v0.2.0-rc.4/docs/THIRD-PARTY-COMPONENTS.md). Distribution rights for any proposed new binary package require a separate review.
