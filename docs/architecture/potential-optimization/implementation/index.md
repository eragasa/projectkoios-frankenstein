# Potential optimization implementation

**Proposed package:** `projectkoios.frankensteins.potential_optimization`

```mermaid
classDiagram
    class MultiObjectiveProblem {
        <<protocol>>
        +validate(candidate)
        +workflow_state(candidate)
        +observe(marking)
        +objectives(observations)
    }
    class PotentialOptimization
    class PotentialModel
    class ParameterSpace
    class StructureDatabase
    class QuantityOfInterestSet
    class MaterialPropertyTarget
    class ObjectiveTransform
    MultiObjectiveProblem <|.. PotentialOptimization
    PotentialOptimization *-- PotentialModel
    PotentialOptimization *-- ParameterSpace
    PotentialOptimization *-- StructureDatabase
    PotentialOptimization *-- QuantityOfInterestSet
    QuantityOfInterestSet *-- MaterialPropertyTarget
    PotentialOptimization *-- ObjectiveTransform
```

```mermaid
flowchart LR
    potential_optimization --> optimization_protocols
    potential_optimization --> potential_models
    potential_optimization --> qoi_models
    potential_optimization --> cpn_workflow_adapter
    historical_configuration_adapter --> potential_optimization
```

`PotentialCandidate` contains independent and fully resolved parameters.
`PotentialEvaluation` retains CPN definition and marking identities, simulation
result references, material-property observations, objective losses, and an
optional classified failure.
