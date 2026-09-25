# Simulation execution implementation

**Proposed packages:** `projectkoios.frankensteins.simulation` and
`projectkoios.frankensteins.integrations.lammps`

```mermaid
classDiagram
    class SimulationBackend {
        <<protocol>>
        +execute(tasks, context) SimulationResult[]
    }
    class SimulationTask
    class ExecutionContext
    class SimulationResult
    class CpnSimulationEffectAdapter {
        +request(binding) SimulationTask
        +external_output(result) ColoredPetriNetBinding
    }
    class ColoredPetriNetBinding
    class LammpsBackend
    class WorkspaceAllocator
    class ProcessRunner
    SimulationBackend <|.. LammpsBackend
    CpnSimulationEffectAdapter --> ColoredPetriNetBinding
    CpnSimulationEffectAdapter --> SimulationTask
    CpnSimulationEffectAdapter --> SimulationResult
    LammpsBackend *-- WorkspaceAllocator
    LammpsBackend *-- ProcessRunner
    LammpsBackend --> SimulationTask
    LammpsBackend --> ExecutionContext
    LammpsBackend --> SimulationResult
```

```mermaid
flowchart LR
    lammps_integration --> simulation_protocols
    lammps_integration --> protected_process_runner
    cpn_effect_runtime --> simulation_protocols
    cpn_effect_runtime --> projectkoios_workflow
    projectkoios_workflow --> projectkoios_cpn
    potential_optimization_cpn_adapter --> simulation_task_models
```

Only the process runner receives command authority. Renderers and parsers remain
deterministic functions over typed inputs and captured artifacts.
