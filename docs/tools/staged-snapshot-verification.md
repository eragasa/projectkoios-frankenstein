# Staged-snapshot verification

`tools/verify_staged_snapshot.py` runs the maintained development verification
sequence against the exact Git index rather than the possibly dirty working
tree. `tools/repository/staged_snapshot.py` owns the typed implementation.

`StagedSnapshotVerifier` records the index tree with `git write-tree`, checks out
the index into a temporary directory, runs the explicitly requested command
sequence there, and removes the directory afterward. It then verifies that the
index tree did not change during execution and runs `git diff --cached --check`.
Unstaged modifications and untracked files are therefore excluded.

The CLI supplies the repository's maintained test, lint, format, strict typing,
and wheel-build commands. Commands use the operator's selected Python
environment but execute with the temporary snapshot as their working directory
and with its `src/` directory on `PYTHONPATH`.

```bash
.venv/bin/python tools/verify_staged_snapshot.py
```

Use `--repository` for another worktree root and `--python` for an explicit
Python executable. The tool does not stage files, mutate the source worktree,
commit changes, or push branches. Tests that require Git metadata need a
separate reviewed design because the temporary checkout intentionally contains
only indexed files and no `.git` directory.
