# Testing

Unit tests verify:

- immutable generic request validation;
- complete generic scope and backend descriptions;
- one description for every represented QE relaxation enum value;
- rejection of QE-documented but unimplemented native values;
- fixed-cell and variable-cell namelist/card composition;
- QE ionic/cell algorithm compatibility;
- registry selection by stable value identity; and
- failure for uninstalled VASP and ABINIT integrations.

These tests establish input-boundary conformance only. They do not establish QE execution, relaxation convergence, force/stress convergence, relaxed-structure correctness, or scientific validation.
