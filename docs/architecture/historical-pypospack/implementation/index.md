# Historical PyPosPack adapter implementation

**Proposed package:** `projectkoios.frankensteins.historical.pypospack`

```mermaid
classDiagram
    class PyPosPackConfigurationAdapter
    class PyPosPackQoiAdapter
    class PyPosPackIterativeOptimizerAdapter
    class PotentialOptimizationConfiguration
    class QoiEvaluator
    class MultiObjectiveOptimizer
    PyPosPackConfigurationAdapter --> PotentialOptimizationConfiguration
    PyPosPackQoiAdapter ..|> QoiEvaluator
    PyPosPackIterativeOptimizerAdapter ..|> MultiObjectiveOptimizer
```

```mermaid
flowchart LR
    historical_pypospack --> maintained_models
    historical_pypospack --> vendored_qoi_runtime
    historical_pypospack --> pinned_pypospack_dependency
    maintained_domain -. no import .-> vendored_qoi_runtime
```

The example launcher currently provides the configuration adapter and QOI package
overlay. These are transitional. The desired package adapter will make every
translation explicit and keep vendored modules outside the maintained domain
namespace.
