# Colored-Petri-net workflow implementation

**Target dependencies:** `projectkoios-cpn` for CPN semantics and
`projectkoios-workflow` for workflow runtime contracts

**Proposed local adapter package:**
`projectkoios.frankensteins.workflows.potential_optimization_cpn`

```mermaid
classDiagram
    class PotentialOptimizationCpnAdapter {
        +fragments(problem) ColoredPetriNetFragment[]
        +compose(problem) ColoredPetriNetComposition
        +initial_marking(problem, candidate) ColoredPetriNetMarking
        +effect_request(binding) SimulationRequest
        +external_output(result) ColoredPetriNetBinding
        +observations(marking) MaterialPropertyObservation[]
    }
    class ColoredPetriNetFragment
    class ColoredPetriNetComposition
    class ColoredPetriNetDefinition
    class ColoredPetriNetMarking
    class ColoredPetriNetTransitionEnabler
    class ColoredPetriNetBindingSelector
    class ColoredPetriNetTransitionFirer
    PotentialOptimizationCpnAdapter --> ColoredPetriNetFragment
    PotentialOptimizationCpnAdapter --> ColoredPetriNetComposition
    ColoredPetriNetComposition --> ColoredPetriNetDefinition
    PotentialOptimizationCpnAdapter --> ColoredPetriNetMarking
    PotentialOptimizationCpnAdapter --> ColoredPetriNetTransitionEnabler
    PotentialOptimizationCpnAdapter --> ColoredPetriNetBindingSelector
    PotentialOptimizationCpnAdapter --> ColoredPetriNetTransitionFirer
```

```mermaid
flowchart TD
    local_scientific_adapter --> projectkoios_cpn
    local_scientific_adapter --> potential_optimization_models
    local_scientific_adapter --> material_property_models
    projectkoios_workflow --> projectkoios_cpn
    effect_runtime --> projectkoios_workflow
    effect_runtime --> simulation_backend
    projectkoios_cpn -. no dependency .-> local_scientific_adapter
```

The current CPN kernel is incubated under
`projectkoios.workflow.petrinet.colored`. That import surface is
non-authoritative shadow evidence and must not become the permanent dependency
of this adapter. Migration targets the accepted `projectkoios-cpn` namespace,
with any temporary compatibility bridge owned and versioned explicitly.
