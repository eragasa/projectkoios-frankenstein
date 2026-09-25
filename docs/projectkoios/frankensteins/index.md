# `projectkoios.frankensteins`

**Source:** `src/projectkoios/frankensteins/`

This package contains provenance-bound reconstructions of selected historical
workflows. It converts verified evidence into immutable observations, recipes,
and closed arithmetic models without importing or executing retained source.

## Package facade

`projectkoios.frankensteins.__init__` re-exports:

- `FrankensteinRecipe`
- `IntegrationObservation`
- `SourceFileEvidence`
- `ObservedSetting`
- `RecipeWarning`

These contracts are implemented by [`core`](core/index.md). The core module also
owns `canonical_json_bytes`, `stable_id`, and `json_payload`; they are imported
from that owning module rather than re-exported by the package facade.

## Modules and subpackages

- [`evidence`](evidence/index.md) owns bounded, descriptor-based reads of
  provenance evidence.
- [`engines`](engines/index.md) reconstructs source-qualified examples.
- [`integrations`](integrations/index.md) owns calculator-format inspection and
  protected command intent.
- [`mathematics`](mathematics/index.md) owns safe scalar-model contracts.
- [`__main__`](__main__/index.md) implements the command-line adapter.

## Target architecture

The [desired architecture](../../architecture/index.md) defines future modules
for multi-objective optimization, potential optimization, QOI evaluation,
simulation execution, reusable CPN fragments and visualization targeted for
`projectkoios-cpn`, `projectkoios-workflow` orchestration adapters, and
historical adapters. Those documents
separate target design from the currently implemented package.

## Safety boundary

The package never grants calculator execution authority. It does not select
pseudopotentials, evaluate arbitrary source expressions, claim scientific
validation, fetch upstream repositories, or turn external sources into supported
dependencies.
