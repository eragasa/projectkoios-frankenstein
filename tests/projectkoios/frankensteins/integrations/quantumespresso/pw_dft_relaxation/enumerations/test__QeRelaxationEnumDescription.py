from __future__ import annotations

import unittest

from projectkoios.frankensteins.integrations.quantumespresso.pw_dft_relaxation import (
    enumerations as qe_enumerations,
)


class QeRelaxationEnumDescriptionTest(unittest.TestCase):
    def test_describes_every_native_enum_value_once(self) -> None:
        expected = {
            (type(value), value.value)
            for enum_type in (
                qe_enumerations.QeRelaxationCalculation,
                qe_enumerations.QeRelaxationIonDynamics,
                qe_enumerations.QeRelaxationCellDynamics,
                qe_enumerations.QeRelaxationCellDegreesOfFreedom,
            )
            for value in enum_type
        }
        described = {
            (type(item.value), item.value.value)
            for item in qe_enumerations.QE_RELAXATION_ENUM_DESCRIPTIONS
        }

        self.assertEqual(described, expected)
        self.assertEqual(
            len(qe_enumerations.QE_RELAXATION_ENUM_DESCRIPTIONS), len(expected)
        )

    def test_records_qe_documented_but_unimplemented_cell_mode(self) -> None:
        descriptions = tuple(
            item
            for item in qe_enumerations.QE_RELAXATION_ENUM_DESCRIPTIONS
            if item.value is qe_enumerations.QeRelaxationCellDynamics.STEEPEST_DESCENT
        )

        self.assertEqual(len(descriptions), 1)
        self.assertIs(
            descriptions[0].status,
            qe_enumerations.QeNativeValueStatus.DOCUMENTED_NOT_IMPLEMENTED_BY_QE,
        )


if __name__ == "__main__":
    unittest.main()
