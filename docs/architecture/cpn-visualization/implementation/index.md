# Colored-Petri-net visualization implementation

**Target generic owner:** `projectkoios-cpn`

**Proposed local adapter:**
`projectkoios.frankensteins.workflows.potential_optimization_cpn.annotations`

```mermaid
classDiagram
    class ColoredPetriNetVisualizer {
        <<protocol>>
        +project(input) ColoredPetriNetView
    }
    class ColoredPetriNetView
    class ColoredPetriNetViewInput
    class ColoredPetriNetAnnotationProvider {
        <<protocol>>
        +place_annotation(identity)
        +transition_annotation(identity)
        +token_annotation(token)
    }
    class PotentialOptimizationAnnotationProvider
    class SvgCpnRenderer
    class InteractiveCpnRenderer
    ColoredPetriNetVisualizer --> ColoredPetriNetViewInput
    ColoredPetriNetVisualizer --> ColoredPetriNetView
    ColoredPetriNetViewInput --> ColoredPetriNetAnnotationProvider
    ColoredPetriNetAnnotationProvider <|.. PotentialOptimizationAnnotationProvider
    SvgCpnRenderer --> ColoredPetriNetView
    InteractiveCpnRenderer --> ColoredPetriNetView
```

```mermaid
flowchart LR
    projectkoios_cpn_kernel --> cpn_view_projection
    workflow_view_projection --> generic_renderers
    local_scientific_annotations --> workflow_view_projection
    local_scientific_annotations --> material_property_models
    generic_renderers -. no dependency .-> scientific_models
```

Until `projectkoios-cpn` accepts a view contract or wire format, the local
architecture should not invent a competing serialized CPN representation. The
current `projectkoios-workflow` shadow may provide transfer fixtures but is not
the permanent visualizer namespace. An
exploratory renderer may consume exact in-memory public records only and must be
labeled experimental.
