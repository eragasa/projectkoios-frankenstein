# Unit-cell charge declarations

`MaterialSystemDeclaration` owns a collection of named
`StructureDeclaration` objects. Each structure contains a
`UnitCellDeclaration` backed directly by PhysKit lattice types.

```python
import numpy as np
from physkit.periodic import DirectLattice3D

lattice = DirectLattice3D(
    a1=np.asarray((1.0, 0.0, 0.0)),
    a2=np.asarray((0.0, 1.0, 0.0)),
    a3=np.asarray((0.0, 0.0, 1.0)),
)
MgO = MaterialSystemDeclaration("MgO")
MgO.add_structure(
    StructureDeclaration.from_stoichiometry(
        "bulk",
        (("Mg", 1), ("O", 1)),
        lattice,
    )
)
MgO.structure("bulk").unit_cell.charge = 0
```

`SpeciesMultiplicity` records each unit-cell composition.
`UnitCellChargeConstraintCompiler` converts one named structure's mutable
charge declaration into an immutable `StoichiometricChargeConstraint`
containing `StoichiometricChargeTerm` and `SpeciesChargeParameter` values.
`StoichiometricChargeConstraintResolver` validates a complete assignment or
produces one missing `ResolvedSpeciesCharge`. `ChargeConstraintError` reports
invalid, underdetermined, or inconsistent declarations and assignments.

The prototype imports PhysKit's `DirectLattice3D` and
`ReciprocalLattice3D`; it does not reconstruct or wrap their lattice geometry.
The reciprocal lattice is derived through PhysKit from each structure's
declared direct lattice.

The compiler, rather than author-written example code, derives
`Mg.charge + O.charge = 0`. Probability distributions and external sampling
bindings are deliberately outside this prototype.
