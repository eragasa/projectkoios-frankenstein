from __future__ import annotations

import unittest

from projectkoios.frankensteins.integrations.quantumespresso.outputs.base import (
    QeOutputFile,
    QeOutputFileParser,
    QeOutputFileResult,
)
from projectkoios.frankensteins.integrations.quantumespresso.outputs.dos import (
    QeDosFile,
    QeDosFileParser,
    QeDosFileResult,
)


class QeDosFileParserTest(unittest.TestCase):
    def test_family_composes_the_nominal_bases(self) -> None:
        self.assertTrue(issubclass(QeDosFile, QeOutputFile))
        self.assertTrue(issubclass(QeDosFileParser, QeOutputFileParser))
        self.assertTrue(issubclass(QeDosFileResult, QeOutputFileResult))

    def test_parser_is_an_explicit_stub(self) -> None:
        output_file = QeDosFile(relative_path="silicon.dos")
        with self.assertRaises(NotImplementedError):
            QeDosFileParser().parse(b"", output_file=output_file)


if __name__ == "__main__":
    unittest.main()
