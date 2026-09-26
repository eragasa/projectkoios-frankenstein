# Common workflow runners

The runners share one `WorkflowRunnerEnvironment` and `WorkflowRunnerConfigurationLoader`:

- `render_inputs.py`: calculator projection;
- `replay.py`: retained-evidence replay through `dft_pw_scf`;
- `plan.py`: convergence coordinate planning;
- `compare_single.py`: qualified single-SCF comparison;
- `compare_convergence.py`: qualified convergence-test comparison;
- `plot_structure.py`: configured structure visualization.

Commands receive campaign, runner configuration, evidence, artifact-root, and output paths explicitly. Calculator selection is source controlled; no dynamic imports are accepted.
