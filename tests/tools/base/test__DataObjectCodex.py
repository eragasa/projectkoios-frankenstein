from __future__ import annotations

import unittest
from dataclasses import dataclass

from tools.base import (
    DataObject,
    DataObjectCodex,
    DataObjectDeserializer,
    DataObjectModel,
    DataObjectSerializer,
)


@dataclass(frozen=True, slots=True)
class _Word(DataObject):
    text: str


@dataclass(frozen=True, slots=True)
class _WordModel(DataObjectModel):
    text: str


class _UpperSerializer(DataObjectSerializer[_Word, _WordModel]):
    def serialize(self, data_object: _Word, /) -> _WordModel:
        return _WordModel(text=data_object.text.upper())


class _LowerSerializer(DataObjectSerializer[_Word, _WordModel]):
    def serialize(self, data_object: _Word, /) -> _WordModel:
        return _WordModel(text=data_object.text.lower())


class _WordDeserializer(DataObjectDeserializer[_WordModel, _Word]):
    def deserialize(self, model: _WordModel, /) -> _Word:
        return _Word(text=model.text)


class _WordCodex(DataObjectCodex[_Word, _WordModel]):
    def serializer(
        self,
        serializer_id: str,
        /,
    ) -> DataObjectSerializer[_Word, _WordModel]:
        if serializer_id == "upper":
            return _UpperSerializer()
        if serializer_id == "lower":
            return _LowerSerializer()
        raise ValueError(f"unknown serializer: {serializer_id}")

    def deserializer(
        self,
        deserializer_id: str,
        /,
    ) -> DataObjectDeserializer[_WordModel, _Word]:
        if deserializer_id == "word":
            return _WordDeserializer()
        raise ValueError(f"unknown deserializer: {deserializer_id}")


class _MissingSerializer(DataObjectSerializer[_Word, _WordModel]):
    pass


class DataObjectCodexTest(unittest.TestCase):
    def test_abstract_serializer_is_enforced_at_runtime(self) -> None:
        with self.assertRaisesRegex(TypeError, "abstract method 'serialize'"):
            _MissingSerializer()

    def test_facade_selects_one_of_multiple_serializers_explicitly(self) -> None:
        codex = _WordCodex()
        data_object = _Word(text="MiXeD")

        upper = codex.serializer("upper").serialize(data_object)
        lower = codex.serializer("lower").serialize(data_object)

        self.assertEqual(upper, _WordModel(text="MIXED"))
        self.assertEqual(lower, _WordModel(text="mixed"))
        self.assertEqual(codex.deserializer("word").deserialize(upper), _Word("MIXED"))


if __name__ == "__main__":
    unittest.main()
