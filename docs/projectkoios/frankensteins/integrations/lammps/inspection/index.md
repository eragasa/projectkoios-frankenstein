# `projectkoios.frankensteins.integrations.lammps.inspection`

**Source:** `.../integrations/lammps/inspection.py`

## `inspect_lammps_templates(...)`

Consumes explicit `lmps_sim_type` settings plus path-keyed evidence and text.
For each setting it:

1. derives `lmp_scripts_db/<declared-directory>`;
2. collects and sorts retained file evidence below that directory;
3. requires `runsimulation.sh` evidence and text;
4. requires exactly one command matching `$LAMMPS_BIN -i INPUT > OUTPUT` or the
   braced environment-variable form;
5. requires the referenced input script to exist; and
6. returns a `LammpsIntegrationObservation` with execution-disabled intents.

The private `_COMMAND` regular expression recognizes only this bounded command
shape. The inspector records intent; it does not expand environment variables,
open files, invoke a shell, or execute LAMMPS.
