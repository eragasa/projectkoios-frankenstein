from __future__ import annotations

import unittest

from projectkoios.frankensteins.integrations.quantumespresso.outputs.base import (
    QeOutputFileParser,
    QeOutputFileResult,
    QuantumEspressoOutputFileError,
)
from projectkoios.frankensteins.integrations.quantumespresso.outputs.pw_stdout import (
    QePwStdoutFile,
    QePwStdoutFileParser,
)

PW_OUTPUT = b"""Program PWSCF v.7.2 starts on  1Jan2026
     number of atoms/cell      =            2
     number of k points=    29
     kinetic-energy cutoff     =      40.0000  Ry
     iteration #  1     ecut=    40.00 Ry
     iteration #  2     ecut=    40.00 Ry
     convergence has been achieved in   2 iterations
!    total energy              =     -15.12300000 Ry
          total   stress  (Ry/bohr**3)                   (kbar)     P=       -0.12
!    total energy              =     -15.12456789 Ry
JOB DONE.
"""


class QePwStdoutFileParserTest(unittest.TestCase):
    def test_parse_uses_native_units_and_last_energy(self) -> None:
        parser = QePwStdoutFileParser()
        output = parser.parse(
            PW_OUTPUT,
            output_file=QePwStdoutFile.from_prefix(prefix="silicon"),
        )

        self.assertIsInstance(parser, QeOutputFileParser)
        self.assertIsInstance(output, QeOutputFileResult)
        self.assertEqual(output.program_version, "7.2")
        self.assertTrue(output.job_completed)
        self.assertTrue(output.scf_converged)
        self.assertEqual(output.total_energy_ry, -15.12456789)
        self.assertEqual(output.wavefunction_cutoff_ry, 40.0)
        self.assertEqual(output.pressure_kbar, -0.12)
        self.assertEqual(output.atom_count, 2)
        self.assertEqual(output.k_point_count, 29)
        self.assertEqual(output.scf_iteration_count, 2)

    def test_parse_accepts_fortran_double_exponents(self) -> None:
        output = QePwStdoutFileParser().parse(
            b"! total energy = -1.234500D+01 Ry\nJOB DONE.\n",
            output_file=QePwStdoutFile.from_prefix(prefix="silicon"),
        )

        self.assertEqual(output.total_energy_ry, -12.345)
        self.assertTrue(output.job_completed)

    def test_parse_rejects_unrecognized_text(self) -> None:
        with self.assertRaisesRegex(
            QuantumEspressoOutputFileError,
            "no supported pw.x stdout observations",
        ):
            QePwStdoutFileParser().parse(
                b"not calculator output\n",
                output_file=QePwStdoutFile.from_prefix(prefix="silicon"),
            )


if __name__ == "__main__":
    unittest.main()
