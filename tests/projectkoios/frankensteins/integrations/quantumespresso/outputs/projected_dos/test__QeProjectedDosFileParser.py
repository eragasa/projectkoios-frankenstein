from __future__ import annotations

import unittest

from projectkoios.frankensteins.integrations.quantumespresso.outputs import (
    projected_dos as projected_dos_output,
)
from projectkoios.frankensteins.integrations.quantumespresso.outputs.base import (
    QeOutputFile,
    QeOutputFileParser,
    QeOutputFileResult,
)


class QeProjectedDosFileParserTest(unittest.TestCase):
    def test_family_composes_the_nominal_bases(self) -> None:
        self.assertTrue(
            issubclass(projected_dos_output.QeProjectedDosFile, QeOutputFile)
        )
        self.assertTrue(
            issubclass(
                projected_dos_output.QeProjectedDosFileParser,
                QeOutputFileParser,
            )
        )
        self.assertTrue(
            issubclass(
                projected_dos_output.QeProjectedDosFileResult,
                QeOutputFileResult,
            )
        )

    def test_parser_is_an_explicit_stub(self) -> None:
        output_file = projected_dos_output.QeProjectedDosFile(
            relative_path="silicon.proj"
        )
        with self.assertRaises(NotImplementedError):
            projected_dos_output.QeProjectedDosFileParser().parse(
                b"", output_file=output_file
            )


if __name__ == "__main__":
    unittest.main()
