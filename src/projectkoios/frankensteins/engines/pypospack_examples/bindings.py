# ruff: noqa: E501
# Exact source paths and Git object identities are intentionally kept literal.

from __future__ import annotations

from dataclasses import dataclass

from projectkoios.frankensteins.engines.base import BaseEngine

_ALLOWED_EXECUTION_SURFACES = {"lammps", "pyposmat", "vasp"}

SOURCE_EXAMPLE_TREES: dict[str, str] = {
    "examples/Al__eam__born_exp_fs/pareto_optimization_3.5NN": "375529a1a104270f189d05f3012f27a775bc09fd",
    "examples/Al__eam__born_exp_fs/preconditioning_3.5NN": "1504e9a7da7cab703935a0d931718b51943eb300",
    "examples/MgO__buck__add_additional_qoi": "a2f0869aa78895e8bc589ff4226d33d547cca0d0",
    "examples/MgO__buck__iterative_sampler": "1a6752c9b97bbe5180cbef4a0be6c7dd750387c3",
    "examples/MgO__buck__lammps_neb/lammps_neb": "99c1bcc2cbf04a3ac292893f8a82ec40abb3e07a",
    "examples/Ni__dft/ni_bcc_cubic": "08d15c4cd192dce12b7fd4c0ff1650bb0249073b",
    "examples/Ni__dft/ni_diamond_cubic": "630f203e60bac79863067f962ff47825f31ba3b7",
    "examples/Ni__dft/ni_fcc_cubic": "ba2ca36d8caa6f98ae999a389b459fc6b33b5107",
    "examples/Ni__dft/ni_hcp_cubic": "514d01d0bb3492f48f898f4692335ee66b4dad48",
    "examples/Ni__dft/ni_sc_vasp": "537dc9f3c58a2e7a5865a5cc022fafc176fbc667",
    "examples/Ni__eam/reference_potentials": "8b2f254640f1f7e6beadff077985bae21b15dc06",
    "examples/Ni__eam__born_exp_fs/pareto_optimization_3.5NN": "2c91db2e3b1aaafd03c188501f9fdaf465752474",
    "examples/Ni__eam__born_exp_fs/preconditioning_3.5NN": "029619941ff4ee5b7c2c1b7837da100e6527cc1d",
    "examples/Ni__eam__born_exp_fs__cluster": "a62b936357cea08baede2c3a80e3ac0be525edb4",
    "examples/Ni__eam__born_exp_fs__sensitivityanalysis/01__dev__normal_parametric_sampling": "1a06d682c7ceffbdf73f98d45acee95ac2fa2c72",
    "examples/Ni__eam__born_exp_rose/00_preconditioning_3.5NN": "35b81839c4d53eb53862d4c9f3b76c9b2ea194eb",
    "examples/Ni__eam__born_exp_rose/01_preconditioning_3.5NN": "164d1cae6f73bedb060276669ee619150b440dad",
    "examples/Ni__eam__born_exp_rose/pareto_optimization_3.5NN": "dcb9f9fdab2515337b248d2bc6f719895122d98a",
    "examples/Ni__eam__glj_rose_Mishin_2004/pareto_optimization_3.5NN": "a6b0db341a428155315551113e728e95dd021a37",
    "examples/Ni__eam__morse_exp_fs/pareto_optimization_3.5NN": "df74574c276f2b20916a61b005e1160982cddfc9",
    "examples/Ni__eam__morse_exp_fs/preconditioning_3.5NN": "899a5873d4fbf6ecc9148ee5fe44d0c53a954b09",
    "examples/Si__sw/dev__pareto_optimization": "886f20feccad98e525bdf967a313e32f3893ffc4",
    "examples/Si__sw/pareto_optimization": "10e21c17457b78e85adebeeefb792b02e19dd39b",
    "examples/Si__sw/pareto_optimization_npt": "f363f2649bc883266557431ed8c6598e6b91790e",
    "examples/Si__sw/pareto_optimization_p_3.5_q_0.5": "cb8011bd8b3346f69bc9458bd66f9d39e59552e5",
    "examples/Si__sw/pareto_optimization_p_4.0_q_0.0": "7fa3b04edab381097dffc25016274dd973e9021c",
    "examples/Si__sw/reference_potentials": "1367df5a16295b7306ad04d0a6c796c204145dd7",
    "examples/Si__tersoff": "fe87360e3b35f722f12a215c79c5a22091344c7c",
    "examples/Si__tersoff/structure_db": "46eac45d61fad2c6f75931b027d4c89aab13fa63",
    "examples/ni_lammps/lmps_scripts_db/min": "bd9143008ed01cbab9eb9e6212214c55b30a1414",
    "examples/ni_vasp_test": "3ff85b38e0f34490c1c2e2b49b2af5a10a2e1e29",
}


@dataclass(frozen=True)
class PypospackExampleEngineBinding(BaseEngine):
    """One exact, statically identified PyPosPack example execution surface."""

    execution_surface: str

    def __post_init__(self) -> None:
        super().__post_init__()
        if SOURCE_EXAMPLE_TREES.get(self.example_root) != self.example_tree:
            raise ValueError("example_tree must match the source tree table")
        if self.execution_surface not in _ALLOWED_EXECUTION_SURFACES:
            raise ValueError("execution_surface is invalid")


def _binding(
    engine_name: str,
    example_root: str,
    entrypoints: tuple[str, ...],
    execution_surface: str,
) -> PypospackExampleEngineBinding:
    return PypospackExampleEngineBinding(
        engine_name=engine_name,
        example_root=example_root,
        example_tree=SOURCE_EXAMPLE_TREES[example_root],
        entrypoints=entrypoints,
        execution_surface=execution_surface,
    )


ENGINE_BINDINGS = (
    _binding(
        "pypospack-al-eam-born-exp-fs-pareto-optimization-3-5nn",
        "examples/Al__eam__born_exp_fs/pareto_optimization_3.5NN",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-al-eam-born-exp-fs-preconditioning-3-5nn",
        "examples/Al__eam__born_exp_fs/preconditioning_3.5NN",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-mgo-buck-add-additional-qoi",
        "examples/MgO__buck__add_additional_qoi",
        ("evaluate_additional_qois.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-mgo-buck-iterative-sampler",
        "examples/MgO__buck__iterative_sampler",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-mgo-buck-lammps-neb",
        "examples/MgO__buck__lammps_neb/lammps_neb",
        ("lammps_neb.py",),
        "lammps",
    ),
    _binding(
        "pypospack-ni-dft-bcc-cubic",
        "examples/Ni__dft/ni_bcc_cubic",
        ("01_initial_minimization.py", "02_conv_kpoints.py", "03_conv_encut.py"),
        "vasp",
    ),
    _binding(
        "pypospack-ni-dft-diamond-cubic",
        "examples/Ni__dft/ni_diamond_cubic",
        ("01_initial_minimization.py",),
        "vasp",
    ),
    _binding(
        "pypospack-ni-dft-fcc-cubic",
        "examples/Ni__dft/ni_fcc_cubic",
        ("01_initial_minimization.py", "02_conv_kpoints.py", "03_conv_encut.py"),
        "vasp",
    ),
    _binding(
        "pypospack-ni-dft-hcp-cubic",
        "examples/Ni__dft/ni_hcp_cubic",
        ("01_initial_minimization.py", "02_conv_kpoints.py", "03_conv_encut.py"),
        "vasp",
    ),
    _binding(
        "pypospack-ni-dft-sc-vasp",
        "examples/Ni__dft/ni_sc_vasp",
        ("01_initial_minimization.py",),
        "vasp",
    ),
    _binding(
        "pypospack-ni-eam-reference-potentials",
        "examples/Ni__eam/reference_potentials",
        ("dev__PyposmatEngine__eam_Ni.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-ni-eam-born-exp-fs-pareto-optimization-3-5nn",
        "examples/Ni__eam__born_exp_fs/pareto_optimization_3.5NN",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-ni-eam-born-exp-fs-preconditioning-3-5nn",
        "examples/Ni__eam__born_exp_fs/preconditioning_3.5NN",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-ni-eam-born-exp-fs-cluster",
        "examples/Ni__eam__born_exp_fs__cluster",
        ("run__iterative_cluster_sampling.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-ni-eam-born-exp-fs-sensitivity-normal-sampling",
        "examples/Ni__eam__born_exp_fs__sensitivityanalysis/01__dev__normal_parametric_sampling",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-ni-eam-born-exp-rose-00-preconditioning-3-5nn",
        "examples/Ni__eam__born_exp_rose/00_preconditioning_3.5NN",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-ni-eam-born-exp-rose-01-preconditioning-3-5nn",
        "examples/Ni__eam__born_exp_rose/01_preconditioning_3.5NN",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-ni-eam-born-exp-rose-pareto-optimization-3-5nn",
        "examples/Ni__eam__born_exp_rose/pareto_optimization_3.5NN",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-ni-eam-glj-rose-mishin-2004-pareto-3-5nn",
        "examples/Ni__eam__glj_rose_Mishin_2004/pareto_optimization_3.5NN",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-ni-eam-morse-exp-fs-pareto-optimization-3-5nn",
        "examples/Ni__eam__morse_exp_fs/pareto_optimization_3.5NN",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-ni-eam-morse-exp-fs-preconditioning-3-5nn",
        "examples/Ni__eam__morse_exp_fs/preconditioning_3.5NN",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-si-sw-dev-pareto-optimization",
        "examples/Si__sw/dev__pareto_optimization",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-si-sw-pareto-optimization",
        "examples/Si__sw/pareto_optimization",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-si-sw-pareto-optimization-npt",
        "examples/Si__sw/pareto_optimization_npt",
        ("evaluate_additional_qois.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-si-sw-pareto-p-3-5-q-0-5",
        "examples/Si__sw/pareto_optimization_p_3.5_q_0.5",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-si-sw-pareto-p-4-0-q-0-0",
        "examples/Si__sw/pareto_optimization_p_4.0_q_0.0",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-si-sw-reference-potentials",
        "examples/Si__sw/reference_potentials",
        ("mc_iterative_sampler.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-si-tersoff",
        "examples/Si__tersoff",
        ("mc_sampler_iterate.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-si-tersoff-structure-db",
        "examples/Si__tersoff/structure_db",
        ("mc_sampler_iterate.py",),
        "pyposmat",
    ),
    _binding(
        "pypospack-ni-lammps-min",
        "examples/ni_lammps/lmps_scripts_db/min",
        ("pypospack_lammps_min.py",),
        "lammps",
    ),
    _binding(
        "pypospack-ni-vasp-test",
        "examples/ni_vasp_test",
        ("calc_bulk_properties.py",),
        "vasp",
    ),
)

_BINDINGS_BY_NAME = {binding.engine_name: binding for binding in ENGINE_BINDINGS}
if len(_BINDINGS_BY_NAME) != len(ENGINE_BINDINGS):
    raise RuntimeError("PyPosPack example engine names must be unique")
if len({binding.example_root for binding in ENGINE_BINDINGS}) != len(ENGINE_BINDINGS):
    raise RuntimeError("PyPosPack example roots must be unique")


def engine_binding(engine_name: str) -> PypospackExampleEngineBinding:
    """Return one exact PyPosPack example binding or reject an unknown name."""

    try:
        return _BINDINGS_BY_NAME[engine_name]
    except KeyError as error:
        raise ValueError(f"unknown PyPosPack example engine: {engine_name}") from error


__all__ = [
    "ENGINE_BINDINGS",
    "SOURCE_EXAMPLE_TREES",
    "PypospackExampleEngineBinding",
    "engine_binding",
]
