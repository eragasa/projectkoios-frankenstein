# Validation implementation

```mermaid
classDiagram
    class ValidationRequest
    class ValidationResult {
        <<abstract>>
        +is_valid bool
    }
    class Validator~RequestT, ResultT~ {
        <<abstract>>
        +validate(request) ResultT
    }
    class UniformProbabilityDistributionSamplerValidationRequest
    class UniformProbabilityDistributionSamplerValidation
    class UniformProbabilityDistributionSamplerValidator
    ValidationRequest <|-- UniformProbabilityDistributionSamplerValidationRequest
    ValidationResult <|-- UniformProbabilityDistributionSamplerValidation
    Validator <|-- UniformProbabilityDistributionSamplerValidator
    UniformProbabilityDistributionSamplerValidator --> UniformProbabilityDistributionSamplerValidationRequest
    UniformProbabilityDistributionSamplerValidator --> UniformProbabilityDistributionSamplerValidation
```

The generic bases live in `projectkoios.frankensteins.validation.base`.
Probability-specific request, result, and validator classes remain beside the
probability sampler they validate.
