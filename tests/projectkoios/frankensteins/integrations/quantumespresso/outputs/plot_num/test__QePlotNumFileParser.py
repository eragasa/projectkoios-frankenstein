from __future__ import annotations

import unittest

from projectkoios.frankensteins.integrations.quantumespresso.outputs.base import (
    QeOutputFile,
    QeOutputFileParser,
    QeOutputFileResult,
)
from projectkoios.frankensteins.integrations.quantumespresso.outputs.plot_num import (
    QePlotNumFile,
    QePlotNumFileParser,
    QePlotNumFileResult,
)


class QePlotNumFileParserTest(unittest.TestCase):
    def test_family_composes_the_nominal_bases(self) -> None:
        self.assertTrue(issubclass(QePlotNumFile, QeOutputFile))
        self.assertTrue(issubclass(QePlotNumFileParser, QeOutputFileParser))
        self.assertTrue(issubclass(QePlotNumFileResult, QeOutputFileResult))

    def test_parser_is_an_explicit_stub(self) -> None:
        output_file = QePlotNumFile(relative_path="silicon.charge.xsf")
        with self.assertRaises(NotImplementedError):
            QePlotNumFileParser().parse(b"", output_file=output_file)


if __name__ == "__main__":
    unittest.main()
