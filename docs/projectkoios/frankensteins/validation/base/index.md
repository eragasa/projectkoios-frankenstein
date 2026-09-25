# Validation framework

`ValidationRequest` is the immutable nominal input base. `ValidationResult` is
the immutable evidence base and requires specialized `is_valid` semantics.
`Validator` is the runtime-enforced action from a request to its result.

The framework does not prescribe generic findings, severity, persistence, or
scheduling. Invalid subjects return domain results; malformed requests or
failed execution raise domain errors.
