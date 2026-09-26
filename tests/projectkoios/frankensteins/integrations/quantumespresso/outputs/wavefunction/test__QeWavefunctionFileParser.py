from __future__ import annotations

import unittest

from projectkoios.frankensteins.integrations.quantumespresso.outputs import (
    wavefunction as wavefunction_output,
)
from projectkoios.frankensteins.integrations.quantumespresso.outputs.base import (
    QeOutputFile,
    QeOutputFileParser,
    QeOutputFileResult,
)


class QeWavefunctionFileParserTest(unittest.TestCase):
    def test_family_composes_the_nominal_bases(self) -> None:
        self.assertTrue(
            issubclass(wavefunction_output.QeWavefunctionFile, QeOutputFile)
        )
        self.assertTrue(
            issubclass(
                wavefunction_output.QeWavefunctionFileParser,
                QeOutputFileParser,
            )
        )
        self.assertTrue(
            issubclass(
                wavefunction_output.QeWavefunctionFileResult,
                QeOutputFileResult,
            )
        )

    def test_parser_is_an_explicit_stub(self) -> None:
        output_file = wavefunction_output.QeWavefunctionFile.from_prefix(
            prefix="silicon", index=2
        )
        self.assertEqual(output_file.relative_path, "silicon.wfc2")
        with self.assertRaises(NotImplementedError):
            wavefunction_output.QeWavefunctionFileParser().parse(
                b"", output_file=output_file
            )

    def test_rejects_invalid_index(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive integer"):
            wavefunction_output.QeWavefunctionFile.from_prefix(
                prefix="silicon", index=0
            )


if __name__ == "__main__":
    unittest.main()
