# `VaspStructureObservation`

**Implemented in:** `projectkoios.frankensteins.integrations.vasp.poscar`

Immutable structural observation bound to `SourceFileEvidence`.

## Fields and invariants

`name` and `comment` are bounded nonempty text, and `evidence` is the retained `SourceFileEvidence`. `scale` remains the original string but must parse as a finite nonzero float. Optional `element_symbols` must align with positive `element_counts`. `coordinate_mode` is normalized to `direct` or `cartesian`, and `coordinate_count` must equal the sum of element counts.

`to_dict()` emits the observation and explicitly sets calculator execution and scientific-validity claims to `False`. It records structure syntax, not a validated physical configuration.
