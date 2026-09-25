from __future__ import annotations

import unittest

from projectkoios.frankensteins.core import ObservedSetting, SourceFileEvidence
from projectkoios.frankensteins.integrations.lammps import inspect_lammps_templates


def evidence(path: str) -> SourceFileEvidence:
    return SourceFileEvidence(path, "0" * 64, 1)


class InspectLammpsTemplatesTest(unittest.TestCase):
    def test_normalizes_a_historical_absolute_lammps_executable(self) -> None:
        runner_path = "lmp_scripts_db/single_point/runsimulation.sh"
        input_path = "lmp_scripts_db/single_point/in.single_point"
        observation = inspect_lammps_templates(
            simulation_settings=(
                ObservedSetting(
                    key="lmps_sim_type",
                    values=("sp", "single_point"),
                    evidence_path="pyposmat.config",
                    line_number=1,
                ),
            ),
            evidence_by_path={
                runner_path: evidence(runner_path),
                input_path: evidence(input_path),
            },
            text_by_path={
                runner_path: (
                    "/home/example/bin/lmp_intx_comb -i in.single_point > out.dat\n"
                ),
            },
        )

        intent = observation.templates[0].command_intent
        self.assertEqual(intent.executable_environment_variable, "LAMMPS_BIN")
        self.assertEqual(intent.input_script, "in.single_point")
        self.assertEqual(intent.stdout_artifact, "out.dat")
        self.assertFalse(intent.execution_authorized)

    def test_rejects_an_unrecognized_absolute_program(self) -> None:
        runner_path = "lmp_scripts_db/single_point/runsimulation.sh"
        input_path = "lmp_scripts_db/single_point/in.single_point"
        with self.assertRaisesRegex(ValueError, "executable is unsupported"):
            inspect_lammps_templates(
                simulation_settings=(
                    ObservedSetting(
                        key="lmps_sim_type",
                        values=("sp", "single_point"),
                        evidence_path="pyposmat.config",
                        line_number=1,
                    ),
                ),
                evidence_by_path={
                    runner_path: evidence(runner_path),
                    input_path: evidence(input_path),
                },
                text_by_path={runner_path: "/bin/echo -i in.single_point > out.dat\n"},
            )


if __name__ == "__main__":
    unittest.main()
