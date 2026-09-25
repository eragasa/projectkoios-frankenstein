# `ksdft2effmass` bulk-silicon reduction target

This page records the external application contract that motivates adaptation of
the reconstructed optimization architecture. It is a target reference, not a
vendored source selection and not authorization to modify or execute the target
repository.

- Repository: `https://github.com/eragasa/ksdft2effmass`
- Inspected commit: `7bd913151f7e61ed2bdba593df920be36573b502`
- Inspected tree: `4f7ca69afbd1381c0cb736b0efe6b8ac5431acf6`

The following committed files were inspected from that revision:

| Role | Path | Git blob |
|---|---|---|
| Conference scientific contract | `docs/publications/conferences/ICMSEP2026/ksdft2effmass.ICMEP2026.abstract.md` | `dfcf5d0ea84a1f81843bd778bea3c8760b66b85d` |
| P01 manuscript record | `docs/publications/papers/ksdft2effmass.P01.md` | `921e5eeb29579c4f359648c92a51afb16580bc68` |
| Pre-results manuscript | `docs/publications/papers/ksdft2effmass.P91/manuscript.tex` | `fb44a14e65de68621011d386d9b10ba00d3107c9` |
| Bulk reduced-model hierarchy | `docs/publications/research-monograph/chapters/07-bulk-reduced-models.tex` | `e53247bcddf56e7cd37082153d1ad4a6e1777ad9` |
| Bulk representation decision | `docs/publications/research-monograph/chapters/08-selecting-bulk-representation.tex` | `37ce7f874105e1c7c63cd88f12216325cce9db23` |

## Target problem

The target is a bulk-silicon reduced-Hamiltonian inverse problem. A converged
PBE Kohn--Sham calculation and validated ten-orbital Wannier Hamiltonian form
the parent reference. Candidate models belong to a frozen hierarchy of
orthogonal `sp3s*` Slater--Koster tight-binding classes.

For each class, candidate parameters are evaluated against two distinct
criteria:

1. a spectral criterion over frozen training bands and selected band-edge
   quantities; and
2. an aligned represented-operator criterion comparing real-space tight-binding
   blocks with the Wannier Hamiltonian.

The principal question is whether one exact candidate Hamiltonian satisfies
both declared tolerances. The decision result is the first class in the frozen
hierarchy containing such a candidate. Separately optimized spectral and
operator candidates are insufficient.

Withheld validation includes band energies, the indirect gap, conduction-valley
position, and longitudinal and transverse electron effective masses. Operator
residuals are resolved by onsite/hopping contribution, orbital block, symmetry
channel, and neighbor shell.

## Relationship to the historical reconstruction

The Ragasa MgO workflow supplies reusable evidence for multidimensional
parameter proposals, forward evaluation, complete objective vectors, Pareto
selection, iterative distribution refinement, failure retention, and replay.
The scientific objects change:

| Historical exemplar | Target adaptation |
|---|---|
| Buckingham potential parameters | Tight-binding Hamiltonian parameters |
| LAMMPS material-property forward evaluation | In-process tight-binding spectral and operator evaluation |
| VASP reference material properties | Quantum ESPRESSO and Wannier90 reference Hamiltonian data |
| Material-property QOI errors | Spectral, band-edge, and aligned-operator residuals |
| Pareto potential ensemble | Spectral/operator candidate and admissible-set exploration |

The target repository's own architecture and scientific records remain
authoritative for target implementation and claims. This repository may provide
reconstructed components and conformance evidence but does not independently
accept a model class, tolerance, alignment, optimizer, result, or scientific
conclusion.
