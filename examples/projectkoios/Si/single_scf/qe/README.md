# Silicon Quantum ESPRESSO single SCF

The compact `campaign.toml` selects stable structure, sampling, projection, and replay declarations. Shared values resolve through `workflow/runner/config/`.

Render deterministic inputs:

```bash
PYTHONPATH=src:. .venv/bin/python \
  examples/projectkoios/Si/single_scf/workflow/runner/render_inputs.py \
  examples/projectkoios/Si/single_scf/qe/campaign.toml \
  --runner-config examples/projectkoios/Si/single_scf/workflow/runner/config/runner.toml \
  --output /tmp/projectkoios-si-qe-scf
```

Replay retained QE evidence without executing QE:

```bash
PYTHONPATH=src:. .venv/bin/python \
  examples/projectkoios/Si/single_scf/workflow/runner/replay.py \
  examples/projectkoios/Si/single_scf/qe/campaign.toml \
  --runner-config examples/projectkoios/Si/single_scf/workflow/runner/config/runner.toml \
  --artifact-root .
```
