# Rationale for this project's QE convergence design

This note records why this project treats k-point sampling, wavefunction cutoff,
charge-density cutoff, and the observed property explicitly when studying
Quantum ESPRESSO convergence.

It is a justification for one project-specific research choice. It is not an
architecture rule, a universal best practice, or a claim that researchers must
use the same design. A fixed-ratio study, a full Cartesian grid, a staged study,
or another design can all be reasonable when their scope and resulting claims
are stated accurately.

## Why the numerical space is three-dimensional here

For the symmetry-preserving silicon mesh family used in this project, the
resolution coordinates are

\[
  (N_k, E_{\mathrm{wfc}}, E_\rho),
\]

where `N_k` denotes mesh density, `ecutwfc = E_wfc` is the wavefunction cutoff,
and `ecutrho = E_rho` is the charge-density and potential cutoff.

The retained 36-point campaign imposed

\[
  E_\rho = 8 E_{\mathrm{wfc}}.
\]

It therefore sampled `(N_k, E_wfc)` on a constrained two-dimensional surface
inside the three-coordinate space. That is a valid convergence study for its
declared fixed-ratio policy. It does not independently answer how results change
with `ecutrho` away from that surface.

This distinction motivates, but does not mandate, treating `ecutrho` as a third
coordinate in later studies.

## Evidence that `ecutrho` is meaningful

The official Quantum ESPRESSO 7.5 `INPUT_PW` definition states that:

- `ecutwfc` is the kinetic-energy cutoff in Ry for wavefunctions;
- `ecutrho` is the kinetic-energy cutoff in Ry for charge density and potential;
- `ecutrho` defaults to four times `ecutwfc`;
- reducing the default for norm-conserving pseudopotentials can introduce noise,
  especially in forces and stress;
- ultrasoft pseudopotentials often need `ecutrho` between eight and twelve times
  `ecutwfc`; and
- PAW and other difficult charge densities require testing rather than reliance
  on one universal ratio.

These statements make an independent `ecutrho` check scientifically reasonable,
especially for an ultrasoft pseudopotential and a calculation that consumes
forces or stress. They do not imply that every study needs a full three-axis
Cartesian grid.

- [Online `INPUT_PW`](https://www.quantum-espresso.org/Doc/INPUT_PW.html)
- [PWscf optimization and dynamics guide](https://www.quantum-espresso.org/Doc/pw_user_guide/node11.html)

The implementation authority consulted locally was the official QE 7.5 source
distribution file `PW/Doc/INPUT_PW.def`.

## Evidence for property-specific checks

G. Prandini, A. Marrazzo, I. E. Castelli, N. Mounet, and N. Marzari,
“Precision and efficiency in solid-state pseudopotential calculations,”
*npj Computational Materials* **4**, 72 (2018), describe the SSSP protocol.
It uses independent criteria including all-electron equations of state and
plane-wave convergence tests for phonon frequencies, band structure, cohesive
energy, and pressure.

This supports the choice to inspect the property needed downstream instead of
assuming that total-energy convergence also establishes force or stress
convergence.

- DOI: [10.1038/s41524-018-0127-2](https://doi.org/10.1038/s41524-018-0127-2)
- Preprint: [arXiv:1806.05609](https://arxiv.org/abs/1806.05609)
- Versioned data: [Materials Cloud SSSP archive](https://archive.materialscloud.org/records/rcyfm-68h65)

The SSSP 1.3.0 PBE efficiency metadata identifies the exact silicon UPF used by
the retained campaign and records `cutoff_wfc = 30 Ry` and
`cutoff_rho = 240 Ry`. These are external reference values under the SSSP
protocol, not universal values for every silicon calculation. The project's
retained `40/320 Ry` point exceeds them but remains qualified only by the total
energy observations actually assessed.

## Evidence relevant to stress

Plane-wave finite-basis effects matter particularly when evaluating stress and
changing a cell. Relevant references include:

1. O. H. Nielsen and R. M. Martin, “First-Principles Calculation of Stress,”
   *Physical Review Letters* **50**, 697–700 (1983).
   [DOI 10.1103/PhysRevLett.50.697](https://doi.org/10.1103/PhysRevLett.50.697)
2. G. P. Francis and M. C. Payne, “Finite basis set corrections to total energy
   pseudopotential calculations,” *Journal of Physics: Condensed Matter* **2**,
   4395–4404 (1990).
   [DOI 10.1088/0953-8984/2/19/007](https://doi.org/10.1088/0953-8984/2/19/007)
3. G.-M. Rignanese, Ph. Ghosez, J.-C. Charlier, J.-P. Michenaud, and X. Gonze,
   “Scaling hypothesis for corrections to total energy and stress in
   plane-wave-based ab initio calculations,” *Physical Review B* **52**,
   8160–8178 (1995).
   [DOI 10.1103/PhysRevB.52.8160](https://doi.org/10.1103/PhysRevB.52.8160)

These works make a stress-sensitive cutoff study a reasonable choice for
variable-cell relaxation. They do not select this project's cutoff or pressure
tolerance.

## The approach chosen for this project

Rather than prescribe an exhaustive exploratory grid as a universal process,
this project can use staged scans followed by a bounded joint check:

1. Record the exact calculator, pseudopotential, physical model, structure,
   sampling family, observables, tolerances, and candidate ranges.
2. Hold a conservatively selected `ecutrho` fixed while scanning `ecutwfc`.
3. Hold the selected `ecutwfc` fixed while scanning `ecutrho`.
4. Hold both cutoffs fixed while scanning the k-point family.
5. Check the selected coordinates together rather than assuming that the staged
   axes are separable.
6. Expand the multidimensional study if the joint check fails or the behavior
   is non-monotone.

One possible local interaction check uses the selected point `(k0, w0, r0)` and
the next higher declared value on each coordinate `(k1, w1, r1)`:

```text
(k0, w0, r0)  (k1, w0, r0)  (k0, w1, r0)  (k0, w0, r1)
(k1, w1, r0)  (k1, w0, r1)  (k0, w1, r1)  (k1, w1, r1)
```

The reason for choosing this approach is pragmatic: staged scans reduce the
initial product-grid cost, while the local corner can reveal individual,
paired, and simultaneous changes near the selected point. The corner is not
proof of global monotonicity, separability, or an infinite-resolution limit.
A full three-dimensional campaign remains a reasonable alternative and becomes
the safer choice when the local check exposes coupling.

For relaxation, the observed quantities should include forces and stress. The
ideal two-atom silicon primitive structure has symmetry-constrained atomic
forces, so zero forces there are not an informative force convergence test. A
force study would need a deliberately chosen force-bearing configuration, and a
stress study would need a deliberately chosen strained or non-equilibrium cell.
This note does not choose those perturbations or their tolerances.

## Scope of the retained evidence

The existing campaign supports finite-grid total-energy convergence under its
fixed `ecutrho / ecutwfc = 8` policy. It does not independently establish
`ecutrho`, force, stress, relaxation, NSCF, band, or Wannier convergence.

That qualification does not invalidate the campaign. It states precisely why a
later relaxation-oriented study may reasonably use a different design.
