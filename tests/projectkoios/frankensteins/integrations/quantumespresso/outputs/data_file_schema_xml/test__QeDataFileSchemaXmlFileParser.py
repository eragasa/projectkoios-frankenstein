from __future__ import annotations

import unittest

from projectkoios.frankensteins.integrations.quantumespresso.outputs import (
    data_file_schema_xml as schema_output,
)
from projectkoios.frankensteins.integrations.quantumespresso.outputs.base import (
    QeOutputFile,
    QeOutputFileParser,
    QeOutputFileResult,
)


class QeDataFileSchemaXmlFileParserTest(unittest.TestCase):
    def test_family_composes_the_nominal_bases(self) -> None:
        self.assertTrue(issubclass(schema_output.QeDataFileSchemaXmlFile, QeOutputFile))
        self.assertTrue(
            issubclass(
                schema_output.QeDataFileSchemaXmlFileParser,
                QeOutputFileParser,
            )
        )
        self.assertTrue(
            issubclass(
                schema_output.QeDataFileSchemaXmlFileResult,
                QeOutputFileResult,
            )
        )

    def test_parser_is_an_explicit_stub(self) -> None:
        output_file = schema_output.QeDataFileSchemaXmlFile.from_save_directory(
            "silicon.save"
        )
        self.assertEqual(output_file.relative_path, "silicon.save/data-file-schema.xml")
        with self.assertRaises(NotImplementedError):
            schema_output.QeDataFileSchemaXmlFileParser().parse(
                b"", output_file=output_file
            )


if __name__ == "__main__":
    unittest.main()
