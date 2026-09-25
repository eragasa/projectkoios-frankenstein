from __future__ import annotations

import numpy as np
from physkit.periodic import DirectLattice3D


def cubic_direct_lattice() -> DirectLattice3D:
    return DirectLattice3D(
        a1=np.asarray((1.0, 0.0, 0.0), dtype=np.float64),
        a2=np.asarray((0.0, 1.0, 0.0), dtype=np.float64),
        a3=np.asarray((0.0, 0.0, 1.0), dtype=np.float64),
    )
