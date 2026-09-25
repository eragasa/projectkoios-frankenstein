# Development tools

Development tools use explicit immutable request and response objects rather
than loosely related function parameters and mutable result dictionaries.

- [Lightweight tool base classes](base.md)
- [Python literal source inspection](source-literal-inspection.md)
- [Staged-snapshot verification](staged-snapshot-verification.md)
- [`revalidate_source_reference.py`](revalidate-source-reference.md)
- [`vendor_source_selection.py`](vendor-source-selection.md)

These contracts apply to repository-development tools. They do not establish a
scientific-domain base class, workflow wire format, or package-runtime service
locator.
