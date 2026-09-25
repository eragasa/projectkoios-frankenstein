# QOI evaluation implementation

**Proposed package:** `projectkoios.frankensteins.material_properties`

```mermaid
classDiagram
    class MaterialPropertyDefinition
    class MaterialPropertyTarget
    class MaterialPropertyObservation
    class QuantityOfInterest
    class MaterialPropertyEvaluator {
        <<protocol>>
        +evaluate(results) MaterialPropertyObservation
    }
    class ObjectiveDefinition
    class ObjectiveTransform {
        <<protocol>>
        +transform(observation, target) float
    }
    QuantityOfInterest *-- MaterialPropertyDefinition
    QuantityOfInterest *-- MaterialPropertyTarget
    MaterialPropertyDefinition --> MaterialPropertyEvaluator
    MaterialPropertyEvaluator --> MaterialPropertyObservation
    ObjectiveDefinition --> ObjectiveTransform
    ObjectiveTransform --> MaterialPropertyObservation
    ObjectiveTransform --> MaterialPropertyTarget
```

```mermaid
flowchart LR
    material_properties --> simulation_result_models
    potential_optimization --> material_properties
    potential_optimization_cpn_adapter --> material_properties
    potential_optimization_cpn_adapter --> projectkoios_cpn
    historical_qoi_adapter --> material_properties
    historical_qoi_adapter --> vendored_pypospack_qoi
```

The CPN adapter maps QOI requirements and observations to tokens and transitions.
The historical adapter translates PyPosPack task dictionaries and QOI values.
Maintained material-property models do not import either vendored modules or CPN
implementation details.
