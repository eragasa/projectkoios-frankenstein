# Local storage

`storage/pseudopotentials/` holds project-local pseudopotentials declared by [`resources.toml`](../resources.toml). Its calculator artifacts are Git-ignored and must never be included in a wheel or source archive. Quantum ESPRESSO pseudopotentials are resolved directly from the separately managed repository under `~/opt/pseudopotentials`; they are not duplicated here.

Current local layout:

```text
storage/pseudopotentials/
└── vasp/
    └── paw-pbe/Si/POTCAR
```

Repository resolution uses the declared basename, byte size, SHA-256, and species identity. Missing or changed artifacts are preflight failures; calculators must not start with an unresolved pseudopotential.

The VASP POTCAR is a licensed external operator resource and remains mode `0600`. The SSSP UPF files under `~/opt/pseudopotentials` remain external scientific inputs. Neither resource is project source code or committed provenance evidence.
