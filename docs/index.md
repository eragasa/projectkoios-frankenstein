# Project Koios Frankenstein documentation

This documentation mirrors the maintained source tree. Package, module, and
class documentation lives at the same nested path as its implementation.

## Scope

[`projectkoios.frankensteins`](projectkoios/frankensteins/index.md) contains
provenance-bound, execution-disabled reconstructions. Exact upstream repository
references live in the top-level `sources/` directory; upstream source itself is
never included in this repository or its distributions.

No source reference authorizes calculator, scheduler, shell, or arbitrary Python
execution. Reconstruction does not imply numerical verification or scientific
validation.

## Sources, development, and security

- [`sources/index.md`](sources/index.md) records exact external pins, current
  release status, local-checkout conventions, and pin-update requirements.
- [`development/index.md`](development/index.md) defines setup, verification,
  external-checkout variables, documentation maintenance, and CI.
- [`security/index.md`](security/index.md) defines trust boundaries, defensive
  controls, and residual limits.

## Maintained package map

- [`projectkoios`](projectkoios/index.md)
  - [`frankensteins`](projectkoios/frankensteins/index.md)
    - [`core`](projectkoios/frankensteins/core/index.md)
    - [`evidence`](projectkoios/frankensteins/evidence/index.md)
    - [`engines`](projectkoios/frankensteins/engines/index.md)
    - [`integrations`](projectkoios/frankensteins/integrations/index.md)
    - [`mathematics`](projectkoios/frankensteins/mathematics/index.md)

## Documentation rule

Every maintained Python module has an `index.md` at its mirrored documentation
path. Every top-level class has a nested `ClassName/index.md`. Tests enforce
module, class, public-symbol, and internal-link coverage.
