# Adapter specifications

- `Adapter` **MUST** be the nominal base class for maintained adapter roles.
- `Binding` and `Integration` **MUST** inherit from `Adapter`.
- A binding **MUST** adapt an imported or deliberately vendored code dependency.
- A binding **MUST NOT** grant external application or service authority.
- An integration **MUST** adapt an external application or service boundary.
- External effects **MUST** remain explicit, bounded, and attributable to an
  integration operation.
- An integration that uses a dependency binding **MUST** contain that binding by
  composition; it **MUST NOT** inherit from the binding.
- A class that performs both responsibilities **MUST** be separated into binding
  and integration roles before becoming a maintained public contract.
- Adapter base classes **MUST NOT** invent a generic `adapt()` method without a
  demonstrated shared operation contract.
- A proposed additional shared base class **MUST** freeze implementation work
  until an explicit architecture discussion accepts its invariant and owner.
- Capability repositories **SHOULD** use provider-oriented names such as
  `projectkoios-github`, not architecture-layer or `external` prefixes.
- Incubated adapter modules **MUST** mirror their intended `projectkoios`
  namespace below `projectkoios.frankensteins`.
- Pick-and-pull migration **MUST NOT** require domain-class renaming or
  inheritance redesign.
- Shared namespace package levels **MUST NOT** provide broad implementation
  re-exports. Leaf facades and explicit composition roots **MAY** re-export
  their accepted public surfaces.
