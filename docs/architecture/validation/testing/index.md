# Validation testing

```mermaid
flowchart LR
    B[Framework base tests] --> D[Domain validator contract tests]
    D --> C[Consumer-owned validation invocation]
    C --> O[Opt-in validation test run]
```

Fast tests establish nominal inheritance, immutability, malformed-request
handling, and deterministic small-fixture behavior. Longer-running validator
invocations live beside their consuming component, use the `validation` Pytest
marker, and are excluded from default check-in verification.
