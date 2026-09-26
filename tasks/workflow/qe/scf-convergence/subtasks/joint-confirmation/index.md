# QE joint convergence confirmation

**Task:** `workflow-qe-joint-convergence-confirmation`

**Status:** Closed — maintained control replayed against retained QE evidence

## Objective

Confirm both high-mesh and high-cutoff edges at one finite grid corner.

## Inputs

Axis observations and a joint policy with increments, maxima, consecutive-delta requirements, and total-job budget.

## Outputs

Confirmed settings, bounded extension request, exhausted outcome, or failure.

## Acceptance

Both edges satisfy the same policy at the same finite corner. Extensions are deterministic and finite. The outcome is not described as an infinite-limit proof.
