# `projectkoios.frankensteins.simulations.dft.base`

`PwDftSimulation` roots one plane-wave DFT simulation in a shared unit cell. `Pseudopotential` is the calculator-neutral pseudopotential metadata base object. `PseudopotentialFile` binds such an object to an exact external file identity. Calculator integrations specialize these nominal types through inheritance.
