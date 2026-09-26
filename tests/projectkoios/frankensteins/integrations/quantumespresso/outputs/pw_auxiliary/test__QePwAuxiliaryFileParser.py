from __future__ import annotations

import unittest

from projectkoios.frankensteins.integrations.quantumespresso.outputs import (
    pw_auxiliary as auxiliary_output,
)
from projectkoios.frankensteins.integrations.quantumespresso.outputs.base import (
    QeOutputFile,
    QeOutputFileParser,
    QeOutputFileResult,
)


class QePwAuxiliaryFileParserTest(unittest.TestCase):
    def test_family_composes_the_nominal_bases(self) -> None:
        self.assertTrue(issubclass(auxiliary_output.QePwAuxiliaryFile, QeOutputFile))
        self.assertTrue(
            issubclass(
                auxiliary_output.QePwAuxiliaryFileParser,
                QeOutputFileParser,
            )
        )
        self.assertTrue(
            issubclass(
                auxiliary_output.QePwAuxiliaryFileResult,
                QeOutputFileResult,
            )
        )

    def test_parser_is_an_explicit_stub(self) -> None:
        output_file = auxiliary_output.QePwAuxiliaryFile.from_prefix(
            prefix="silicon",
            suffix="occupations",
        )
        self.assertEqual(output_file.relative_path, "silicon.occupations")
        with self.assertRaises(NotImplementedError):
            auxiliary_output.QePwAuxiliaryFileParser().parse(
                b"", output_file=output_file
            )


if __name__ == "__main__":
    unittest.main()
