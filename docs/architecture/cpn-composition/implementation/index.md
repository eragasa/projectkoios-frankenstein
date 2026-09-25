# Reusable CPN composition implementation

**Target generic owner:** `projectkoios-cpn`

**Proposed scientific fragment package:**
`projectkoios.frankensteins.workflows.fragments`

```mermaid
classDiagram
    class ColoredPetriNetFragmentTemplate {
        <<abstract>>
        +template_identity
        +base_template_identity
        +instantiate(namespace, parameters) ColoredPetriNetFragment
    }
    class ExternalEffectFragmentTemplate
    class SimulationEffectFragmentTemplate
    class MaterialPropertyFragmentTemplate
    class ElasticPropertyFragmentTemplate
    class DefectFormationEnergyFragmentTemplate
    class SurfaceEnergyFragmentTemplate
    ColoredPetriNetFragmentTemplate <|-- ExternalEffectFragmentTemplate
    ExternalEffectFragmentTemplate <|-- SimulationEffectFragmentTemplate
    ColoredPetriNetFragmentTemplate <|-- MaterialPropertyFragmentTemplate
    MaterialPropertyFragmentTemplate <|-- ElasticPropertyFragmentTemplate
    MaterialPropertyFragmentTemplate <|-- DefectFormationEnergyFragmentTemplate
    MaterialPropertyFragmentTemplate <|-- SurfaceEnergyFragmentTemplate
```

```mermaid
classDiagram
    class ColoredPetriNetFragment {
        +identity
        +template_identity
        +inheritance_chain
        +colors
        +places
        +transitions
        +arcs
        +ports
    }
    class ColoredPetriNetPort
    class ColoredPetriNetConnection
    class ColoredPetriNetComposer {
        +compose(fragments, connections) ColoredPetriNetComposition
    }
    class ColoredPetriNetComposition {
        +definition
        +fragment_map
        +composition_evidence
    }
    ColoredPetriNetFragmentTemplate --> ColoredPetriNetFragment
    ColoredPetriNetFragment *-- ColoredPetriNetPort
    ColoredPetriNetConnection --> ColoredPetriNetPort
    ColoredPetriNetComposer --> ColoredPetriNetFragment
    ColoredPetriNetComposer --> ColoredPetriNetConnection
    ColoredPetriNetComposer --> ColoredPetriNetComposition
```

```mermaid
flowchart LR
    projectkoios_cpn_templates --> projectkoios_cpn_kernel
    scientific_template_subclasses --> projectkoios_cpn_templates
    material_property_definitions --> scientific_template_subclasses
    instantiated_fragments --> projectkoios_cpn_composer
    composition_annotations --> cpn_visualizer
```

The current kernel is incubated under
`projectkoios.workflow.petrinet.colored`; it is transfer evidence rather than
the target import namespace. Template inheritance is separate from kernel
inheritance. The public
`ColoredPetriNetDefinition`, marking, validator, enabler, selector, and firer
objects remain exact immutable workflow-kernel types and are not subclassed.
Derived templates extend through validated declarations rather than arbitrary
mutation of inherited fragment internals.
