# Validation specifications

- Validation requests **MUST** be immutable and contain complete criteria and
  replay controls.
- Validation results **MUST** be immutable evidence and define `is_valid` using
  domain-owned criteria.
- Validators **MUST** accept one typed request and return its typed result.
- A subject that fails criteria **MUST** produce an invalid result rather than
  masquerade as malformed input or execution failure.
- Malformed requests and failed execution **MUST** raise domain-specific errors.
- The framework **MUST NOT** imply reconstruction conformance, numerical
  verification, scientific validation, uncertainty qualification, or human
  acceptance beyond the exact criteria represented by a specialized result.
