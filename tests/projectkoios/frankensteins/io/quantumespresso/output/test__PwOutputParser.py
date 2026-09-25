from __future__ import annotations

import unittest

from projectkoios.frankensteins.io.quantumespresso.output import (
    PwOutputParser,
    QuantumEspressoOutputError,
)

PW_OUTPUT = """Program PWSCF v.7.2 starts on  1Jan2026
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


class PwOutputParserTest(unittest.TestCase):
    def test_parse_uses_native_units_and_last_energy(self) -> None:
        output = PwOutputParser().parse(PW_OUTPUT)

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
        output = PwOutputParser().parse(
            "! total energy = -1.234500D+01 Ry\nJOB DONE.\n"
        )

        self.assertEqual(output.total_energy_ry, -12.345)
        self.assertTrue(output.job_completed)

    def test_parse_rejects_unrecognized_text(self) -> None:
        with self.assertRaisesRegex(
            QuantumEspressoOutputError, "no supported pw.x output observations"
        ):
            PwOutputParser().parse("not calculator output\n")


if __name__ == "__main__":
    unittest.main()
