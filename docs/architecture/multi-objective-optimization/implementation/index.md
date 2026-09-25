# Multi-objective optimization implementation

**Proposed package:** `projectkoios.frankensteins.optimization`

```mermaid
classDiagram
    class MultiObjectiveOptimizer {
        <<protocol>>
        +ask() Candidate[]
        +tell(Evaluation[])
        +checkpoint() OptimizerState
    }
    class IterativeSamplingOptimizer
    class SamplingStrategy
    class ParametricSampling
    class KdeSampling
    class FromFileSampling
    class SelectionStrategy
    class ParetoSelection
    MultiObjectiveOptimizer <|.. IterativeSamplingOptimizer
    IterativeSamplingOptimizer *-- SamplingStrategy
    SamplingStrategy <|.. ParametricSampling
    SamplingStrategy <|.. KdeSampling
    SamplingStrategy <|.. FromFileSampling
    IterativeSamplingOptimizer *-- SelectionStrategy
    SelectionStrategy <|.. ParetoSelection
```

```mermaid
flowchart LR
    optimization --> models
    optimization --> problem_protocols
    historical_optimizer_adapter --> optimization
    workflow_orchestration --> optimization
```

The protocol uses immutable candidates, evaluations, objective vectors, and
checkpoints. Historical PyPosPack state is translated by an adapter rather than
exposed through this package.
