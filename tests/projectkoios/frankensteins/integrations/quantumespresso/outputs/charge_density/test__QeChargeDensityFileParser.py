from __future__ import annotations

import unittest

from projectkoios.frankensteins.integrations.quantumespresso.outputs import (
    charge_density as charge_density_output,
)
from projectkoios.frankensteins.integrations.quantumespresso.outputs.base import (
    QeOutputFile,
    QeOutputFileParser,
    QeOutputFileResult,
)


class QeChargeDensityFileParserTest(unittest.TestCase):
    def test_family_composes_the_nominal_bases(self) -> None:
        self.assertTrue(
            issubclass(charge_density_output.QeChargeDensityFile, QeOutputFile)
        )
        self.assertTrue(
            issubclass(
                charge_density_output.QeChargeDensityFileParser,
                QeOutputFileParser,
            )
        )
        self.assertTrue(
            issubclass(
                charge_density_output.QeChargeDensityFileResult,
                QeOutputFileResult,
            )
        )

    def test_parser_is_an_explicit_stub(self) -> None:
        output_file = charge_density_output.QeChargeDensityFile.from_prefix(
            prefix="silicon"
        )
        self.assertEqual(output_file.relative_path, "silicon.rho")
        with self.assertRaises(NotImplementedError):
            charge_density_output.QeChargeDensityFileParser().parse(
                b"", output_file=output_file
            )


if __name__ == "__main__":
    unittest.main()
