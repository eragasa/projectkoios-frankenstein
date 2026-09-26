# Subtask: QE relaxation input projection

**Status:** Closed — typed QE card projection implemented

Render accepted `relax` or `vc-relax` declarations into deterministic QE 7.5 `pw.x` input with explicit `&CONTROL`, `&IONS`, and applicable `&CELL` fields.

**Acceptance:** no unreviewed numerical or path defaults are introduced.

Implementation composes typed `&CONTROL`, `&SYSTEM`, `&ELECTRONS`, `&IONS`, optional `&CELL`, `ATOMIC_SPECIES`, `CELL_PARAMETERS`, `ATOMIC_POSITIONS`, and `K_POINTS` declarations. Native enum values have reviewed context and support descriptions.
