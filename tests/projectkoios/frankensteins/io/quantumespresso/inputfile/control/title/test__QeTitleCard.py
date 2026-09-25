from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from projectkoios.frankensteins.io.quantumespresso.inputfile.base import QeControlCard
from projectkoios.frankensteins.io.quantumespresso.inputfile.control.title import (
    QeTitleCard,
)


class QeTitleCardTest(unittest.TestCase):
    def test_defaults_to_one_blank_character(self) -> None:
        card = QeTitleCard()

        self.assertIsInstance(card, QeControlCard)
        self.assertEqual(card.title, " ")
        self.assertEqual(card.lines, ("title = ' '",))
        self.assertEqual(card.tag, "&CONTROL")

    def test_preserves_a_plain_ascii_title(self) -> None:
        card = QeTitleCard("Silicon SCF")

        self.assertEqual(card.title, "Silicon SCF")
        self.assertEqual(card.lines, ("title = 'Silicon SCF'",))

    def test_rejects_unsafe_title_text(self) -> None:
        with self.assertRaisesRegex(ValueError, "unquoted"):
            QeTitleCard("Silicon's SCF")
        with self.assertRaisesRegex(ValueError, "line terminators"):
            QeTitleCard("Silicon\nSCF")
        with self.assertRaisesRegex(ValueError, "ASCII"):
            QeTitleCard("Silicón")

    def test_is_immutable_and_slotted(self) -> None:
        card = QeTitleCard()

        self.assertFalse(hasattr(card, "__dict__"))
        with self.assertRaises(FrozenInstanceError):
            card.title = "changed"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
