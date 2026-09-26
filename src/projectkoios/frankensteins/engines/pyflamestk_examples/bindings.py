from __future__ import annotations

from dataclasses import dataclass

from projectkoios.frankensteins.engines import base as engine_base

_ALLOWED_STATUSES = {"reconstructable", "blocked"}

SOURCE_EXAMPLE_TREES: dict[str, str] = {
    (
        "examples/MgO_buckingham/lmps_MgO_mpi_iterate"
    ): "92b7fe8aaceb5a2ed1d376463aedb5ab0124dd5c",
    (
        "examples/MgO_buckingham/lmps_MgO_mpi_kde"
    ): "a08b80334a12cf3ceb678cbc6d33994972736d23",
    (
        "examples/MgO_buckingham/lmps_MgO_mpi_uniform"
    ): "502dfc0fd8261a5f66b4bfce9a7eb2f8caaf1361",
    (
        "examples/MgO_buckingham/lmps_MgO_pareto_iterate"
    ): "d5c9064ed72e30cf393dc5adad2462fa9ed81e5a",
    (
        "examples/MgO_buckingham/lmps_MgO_serial_iterate"
    ): "07bab44335d5e446511ec16bc5d97dc9450a554e",
    (
        "examples/MgO_buckingham/lmps_MgO_serial_single"
    ): "c8e13e093f13c96fb5173af983cd7ff135dd9d61",
    (
        "examples/MgO_buckingham/lmps_MgO_serial_uniform"
    ): "622aba661c91e4bea0051395ce2a386f30f56dd0",
    (
        "examples/Si_tersoff/lmps_MgO_pareto_iterate"
    ): "d5c9064ed72e30cf393dc5adad2462fa9ed81e5a",
    (
        "examples/Si_tersoff/lmps_MgO_serial_iterate"
    ): "6ddcbbfdca6c7110bddd16c1d1fa80f326bf2035",
    (
        "examples/Si_tersoff/lmps_Si_serial_pareto"
    ): "a9836ccd2bee7f67ca8223ce26117397ea9361f5",
    "examples/lmps_MgO_mpi_uniform": "502dfc0fd8261a5f66b4bfce9a7eb2f8caaf1361",
    "examples/lmps_MgO_pareto_iterate": "f5804ea04f1a00be400cbe3a3f01dfd412e25172",
    "examples/lmps_MgO_regression_tests": "47f1ef4aeee74acd79475d756b7ffc1aeb98675d",
    "examples/lmps_MgO_sample_file": "900a216c221ecf4c54bb390d8eb03b48e07e54b9",
    "examples/lmps_MgO_serial_kde": "9f5a2a5d6bd6a4b2840238a96d90d92468a21e25",
    "examples/lmps_MgO_serial_uniform": "428adc8f8dd84381e87e34256f7c34e8570ab878",
    "examples/lmps_MgO_surface": "eab477e810716ccfb13a6021be57c6ffc50f0627",
}


@dataclass(frozen=True, slots=True)
class PyflamestkExampleEngineBinding(engine_base.BaseEngine):
    """Immutable reconstruction disposition for one historical example engine."""

    status: str
    limitations: tuple[str, ...] = ()
    content_alias_of: str | None = None

    def __post_init__(self) -> None:
        super(PyflamestkExampleEngineBinding, self).__post_init__()
        if SOURCE_EXAMPLE_TREES.get(self.example_root) != self.example_tree:
            raise ValueError("example_tree must match the source tree table")
        if self.status not in _ALLOWED_STATUSES:
            raise ValueError("status is invalid")
        if self.status == "blocked" and not self.limitations:
            raise ValueError("blocked bindings require limitations")
        if self.status == "reconstructable" and self.limitations:
            raise ValueError("reconstructable bindings cannot retain blockers")
        if self.content_alias_of is not None:
            self._validate_engine_name(self.content_alias_of, "content_alias_of")


ENGINE_BINDINGS = (
    PyflamestkExampleEngineBinding(
        "pyflamestk-mgo-buckingham-mpi-iterate",
        "examples/MgO_buckingham/lmps_MgO_mpi_iterate",
        SOURCE_EXAMPLE_TREES["examples/MgO_buckingham/lmps_MgO_mpi_iterate"],
        ("MgO_buckingham_iterate_mpi.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-mgo-buckingham-mpi-kde",
        "examples/MgO_buckingham/lmps_MgO_mpi_kde",
        SOURCE_EXAMPLE_TREES["examples/MgO_buckingham/lmps_MgO_mpi_kde"],
        ("call_LAMMPS_concurrently.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-mgo-buckingham-mpi-uniform",
        "examples/MgO_buckingham/lmps_MgO_mpi_uniform",
        SOURCE_EXAMPLE_TREES["examples/MgO_buckingham/lmps_MgO_mpi_uniform"],
        ("call_LAMMPS_concurrently.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-mgo-buckingham-pareto-iterate",
        "examples/MgO_buckingham/lmps_MgO_pareto_iterate",
        SOURCE_EXAMPLE_TREES["examples/MgO_buckingham/lmps_MgO_pareto_iterate"],
        ("buckingham_iterate.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-mgo-buckingham-serial-iterate",
        "examples/MgO_buckingham/lmps_MgO_serial_iterate",
        SOURCE_EXAMPLE_TREES["examples/MgO_buckingham/lmps_MgO_serial_iterate"],
        ("buckingham_iterate.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-mgo-buckingham-serial-single",
        "examples/MgO_buckingham/lmps_MgO_serial_single",
        SOURCE_EXAMPLE_TREES["examples/MgO_buckingham/lmps_MgO_serial_single"],
        ("buckingham_single.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-mgo-buckingham-serial-uniform",
        "examples/MgO_buckingham/lmps_MgO_serial_uniform",
        SOURCE_EXAMPLE_TREES["examples/MgO_buckingham/lmps_MgO_serial_uniform"],
        ("buckingham_pareto.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-si-tersoff-mgo-pareto-iterate",
        "examples/Si_tersoff/lmps_MgO_pareto_iterate",
        SOURCE_EXAMPLE_TREES["examples/Si_tersoff/lmps_MgO_pareto_iterate"],
        ("buckingham_iterate.py",),
        "reconstructable",
        content_alias_of="pyflamestk-mgo-buckingham-pareto-iterate",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-si-tersoff-mgo-serial-iterate",
        "examples/Si_tersoff/lmps_MgO_serial_iterate",
        SOURCE_EXAMPLE_TREES["examples/Si_tersoff/lmps_MgO_serial_iterate"],
        ("buckingham_iterate.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-si-tersoff-si-serial-pareto",
        "examples/Si_tersoff/lmps_Si_serial_pareto",
        SOURCE_EXAMPLE_TREES["examples/Si_tersoff/lmps_Si_serial_pareto"],
        ("buckingham_pareto.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-legacy-mgo-mpi-uniform",
        "examples/lmps_MgO_mpi_uniform",
        SOURCE_EXAMPLE_TREES["examples/lmps_MgO_mpi_uniform"],
        ("call_LAMMPS_concurrently.py",),
        "reconstructable",
        content_alias_of="pyflamestk-mgo-buckingham-mpi-uniform",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-legacy-mgo-pareto-iterate",
        "examples/lmps_MgO_pareto_iterate",
        SOURCE_EXAMPLE_TREES["examples/lmps_MgO_pareto_iterate"],
        ("buckingham_iterate.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-legacy-mgo-regression-tests",
        "examples/lmps_MgO_regression_tests",
        SOURCE_EXAMPLE_TREES["examples/lmps_MgO_regression_tests"],
        ("make_regression_test.py", "regression_test.py"),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-legacy-mgo-sample-file",
        "examples/lmps_MgO_sample_file",
        SOURCE_EXAMPLE_TREES["examples/lmps_MgO_sample_file"],
        ("buckingham_sample_file.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-legacy-mgo-serial-kde",
        "examples/lmps_MgO_serial_kde",
        SOURCE_EXAMPLE_TREES["examples/lmps_MgO_serial_kde"],
        ("buckingham_kde.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-legacy-mgo-serial-uniform",
        "examples/lmps_MgO_serial_uniform",
        SOURCE_EXAMPLE_TREES["examples/lmps_MgO_serial_uniform"],
        ("buckingham_uniform.py",),
        "reconstructable",
    ),
    PyflamestkExampleEngineBinding(
        "pyflamestk-legacy-mgo-surface",
        "examples/lmps_MgO_surface",
        SOURCE_EXAMPLE_TREES["examples/lmps_MgO_surface"],
        ("make_regression_test.py", "poscar_make_surface.py", "regression_test.py"),
        "blocked",
        ("The historical QOI vocabulary is unsupported by the bound QOI module.",),
    ),
)

_BINDINGS_BY_NAME = {binding.engine_name: binding for binding in ENGINE_BINDINGS}
if len(_BINDINGS_BY_NAME) != len(ENGINE_BINDINGS):
    raise RuntimeError("PyFlamestk example engine names must be unique")
for _binding in ENGINE_BINDINGS:
    if (
        _binding.content_alias_of is not None
        and _binding.content_alias_of not in _BINDINGS_BY_NAME
    ):
        raise RuntimeError("PyFlamestk content alias target is missing")


def engine_binding(engine_name: str) -> PyflamestkExampleEngineBinding:
    """Return one exact engine binding or reject an unknown name."""

    try:
        return _BINDINGS_BY_NAME[engine_name]
    except KeyError as error:
        raise ValueError(f"unknown PyFlamestk example engine: {engine_name}") from error


__all__ = [
    "ENGINE_BINDINGS",
    "SOURCE_EXAMPLE_TREES",
    "PyflamestkExampleEngineBinding",
    "engine_binding",
]
