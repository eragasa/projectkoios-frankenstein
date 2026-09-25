# Potential optimization implementation

**Incubation package:** `projectkoios.frankensteins.potential_optimization`

```mermaid
classDiagram
    class PotentialOptimization
    class InteratomicPotential
    class InteratomicPotentialParameters
    class ParameterSpace
    class StructureSet
    class QuantityOfInterestSet
    class ReferenceQoiSet
    class ObjectiveTransform
    class ForwardFunctionExecutionEngine
    class PotentialFunctionalEvaluation
    class PotentialResultsHandler
    PotentialOptimization *-- ParameterSpace
    PotentialOptimization *-- StructureSet
    PotentialOptimization *-- QuantityOfInterestSet
    PotentialOptimization *-- ReferenceQoiSet
    PotentialOptimization *-- ObjectiveTransform
    InteratomicPotential *-- InteratomicPotentialParameters
    ForwardFunctionExecutionEngine --> InteratomicPotential
    ForwardFunctionExecutionEngine --> StructureSet
    ForwardFunctionExecutionEngine --> QuantityOfInterestSet
    ForwardFunctionExecutionEngine --> PotentialFunctionalEvaluation
    PotentialResultsHandler --> PotentialFunctionalEvaluation
    PotentialResultsHandler --> ReferenceQoiSet
    PotentialResultsHandler --> ObjectiveTransform
```

```mermaid
flowchart LR
    optimization_engine --> parameter_space
    parameter_space --> resolved_potential
    resolved_potential --> forward_function_execution_engine
    structures --> forward_function_execution_engine
    qoi_definitions --> forward_function_execution_engine
    forward_function_execution_engine --> raw_observations
    predicted_qoi_observations --> potential_results_handler
    precomputed_reference_qois --> potential_results_handler
    potential_results_handler --> optimization_engine
```

`InteratomicPotentialParameters` contains one complete immutable candidate after
independent, fixed, and dependent values have been resolved.
`PotentialFunctionalEvaluation` retains simulation-plan and workflow identities,
calculator evidence, raw material-property observations, and an optional
classified failure. `PotentialResultsHandler` derives objective feedback without
discarding that evaluation evidence.
