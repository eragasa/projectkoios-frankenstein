# QE k-point convergence workflow

**Task:** `workflow-qe-kpoint-convergence`

**Status:** Maintained control path; retained evidence requires repair

## Objective

Assess neighboring total-energy changes as cubic mesh density increases at one declared finite cutoff.

## Inputs

Fixed cutoff, initial meshes, mesh increment, tolerance, consecutive-increment requirement, maximum mesh, and total-job budget.

## Outputs

Ordered SCF child outcomes, tail deltas per atom, and accepted, extend, exhausted, or failed outcome.

## Acceptance

Every coordinate carries structure, mesh, cutoff, executable, pseudopotential, and native-artifact identities. Acceptance uses the declared number of consecutive neighboring deltas.

## Non-goals

Wannier uniform-mesh convergence or an infinite-k-point-limit claim.
