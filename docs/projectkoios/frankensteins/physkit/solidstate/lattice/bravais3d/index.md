# `bravais3d`

Calculator-neutral dimensionless three-dimensional Bravais direct-lattice conventions implemented by `BravaisLatticeKind` and `BravaisLattice`. Physical cell vectors are obtained by multiplying the matrix `A` by the true lattice parameter.

The vector formulas follow the Quantum ESPRESSO 7.5 `ibrav` convention where that convention selects a specific primitive-vector orientation. QE integer parsing and parameter-family rules remain in `io.quantumespresso.inputfile.ibrav`.
