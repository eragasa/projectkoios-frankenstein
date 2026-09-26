# Silicon single-SCF comparator

`comparison.toml` declares campaign identities and explicit energy treatment. Run the common comparator without rerunning either calculator:

```bash
PYTHONPATH=src:. .venv/bin/python \
  examples/projectkoios/Si/single_scf/workflow/runner/compare_single.py \
  examples/projectkoios/Si/single_scf/comparator/comparison.toml \
  --runner-config examples/projectkoios/Si/single_scf/workflow/runner/config/runner.toml \
  --artifact-root .
```

The result is qualified and descriptive; it does not assign calculator equivalence.
