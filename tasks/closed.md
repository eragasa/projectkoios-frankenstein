# Closed tasks

Closed tasks have a recorded terminal outcome and links to exact implementation or termination evidence.

## Calculator-selectable relaxation input

- [Generic structural-relaxation input wrapper](workflow/dft/structural-relaxation/index.md)
- [QE typed input-projection subtask](qe/structural-relaxation/subtasks/input-projection/index.md)

This closes input declaration and selection only. It does not accept a bulk-silicon relaxation policy or implement output analysis, replay, or execution.

## Bulk-silicon SCF convergence

- [Retained QE SCF convergence evidence](qe/retained-scf-convergence-evidence/index.md)
- [QE SCF convergence workflow](workflow/qe/scf-convergence/index.md)
- [Completed end-to-end slice](../slices/bulk-silicon-qe/scf-convergence/index.md)

The terminal technical outcome is finite-grid total-energy policy acceptance at mesh density `14` and wavefunction cutoff `40 Ry`. It does not authorize calculator execution or establish convergence for other properties.
