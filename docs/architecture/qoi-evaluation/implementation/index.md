# QOI evaluation implementation

**Proposed package:** `projectkoios.frankensteins.material_properties`

```mermaid
classDiagram
    class MaterialPropertyDefinition
    class MaterialPropertyObservation
    class QuantityOfInterestDefinition
    class MaterialPropertyEvaluator {
        <<abstract>>
        +evaluate(results) MaterialPropertyObservation
    }
    class ReferenceQoiSet
    class PredictedQoiSet
    class QoiObservationSource
    class ObjectiveDefinition
    class ObjectiveTransform {
        <<abstract>>
        +transform(predicted, reference) float
    }
    QuantityOfInterestDefinition *-- MaterialPropertyDefinition
    MaterialPropertyDefinition --> MaterialPropertyEvaluator
    MaterialPropertyEvaluator --> MaterialPropertyObservation
    ReferenceQoiSet *-- MaterialPropertyObservation
    PredictedQoiSet *-- MaterialPropertyObservation
    MaterialPropertyObservation --> QoiObservationSource
    ObjectiveDefinition --> ObjectiveTransform
    ObjectiveTransform --> MaterialPropertyObservation
```

```mermaid
flowchart LR
    qoi_definitions --> lammps_simulation_planner
    qoi_definitions --> vasp_simulation_planner
    lammps_simulation_results --> material_property_evaluators
    vasp_simulation_results --> material_property_evaluators
    material_property_evaluators --> predicted_qoi_set
    material_property_evaluators --> reference_qoi_set
    predicted_qoi_set --> results_handler
    reference_qoi_set --> results_handler
```

The same maintained property evaluator may consume normalized primitive results
from either backend when the scientific formula is genuinely shared. Backend
adapters remain responsible for parsing and normalizing calculator-specific
artifacts. Every observation retains its source model, backend, structure, task,
artifact, units, and QOI identities.

The CPN adapter maps QOI requirements and observations to tokens and transitions.
Historical adapters translate PyPosPack task dictionaries and QOI values.
Maintained material-property models do not import vendored modules, calculator
integrations, or CPN implementation details.
