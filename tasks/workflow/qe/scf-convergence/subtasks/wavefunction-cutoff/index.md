# QE wavefunction-cutoff convergence workflow

**Task:** `workflow-qe-cutoff-convergence`

**Status:** Maintained control path; retained evidence requires repair

## Objective

Assess neighboring total-energy changes as wavefunction cutoff increases at one declared finite mesh.

## Inputs

Fixed mesh, initial cutoffs, cutoff increment, charge-density ratio, tolerance, consecutive-increment requirement, maximum cutoff, and total-job budget.

## Outputs

Ordered SCF child outcomes, tail deltas per atom, and accepted, extend, exhausted, or failed outcome.

## Acceptance

Native cutoff values and unit conversion evidence are retained. Pseudopotential-specific cutoff meaning remains explicit.

## Non-goals

Force/stress convergence or cross-calculator basis-equivalence claims.
