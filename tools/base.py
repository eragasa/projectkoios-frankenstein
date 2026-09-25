"""Lightweight immutable roles shared by repository-development tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DataObject:
    """Immutable, effect-free represented state."""


@dataclass(frozen=True, slots=True)
class DataObjectModel(DataObject):
    """Optional model representation of a data object."""


@dataclass(frozen=True, slots=True)
class DataObjectRequest(DataObject):
    """Explicit immutable input for one actionizer invocation."""


@dataclass(frozen=True, slots=True)
class DataObjectResult(DataObject):
    """Immutable closed result of one actionizer invocation."""


class DataObjectActionizer[
    RequestT: DataObjectRequest,
    ResultT: DataObjectResult,
](ABC):
    """One runtime-enforced operation from a request to a result."""

    @abstractmethod
    def actionize(self, request: RequestT, /) -> ResultT:
        """Perform the requested operation."""


class DataObjectSerializer[
    ObjectT: DataObject,
    ModelT: DataObjectModel,
](ABC):
    """Convert a data object into one model representation."""

    @abstractmethod
    def serialize(self, data_object: ObjectT, /) -> ModelT:
        """Return a model representation of the data object."""


class DataObjectDeserializer[
    ModelT: DataObjectModel,
    ObjectT: DataObject,
](ABC):
    """Reconstruct a data object from one model representation."""

    @abstractmethod
    def deserialize(self, model: ModelT, /) -> ObjectT:
        """Return the data object represented by the model."""


class DataObjectCodex[
    ObjectT: DataObject,
    ModelT: DataObjectModel,
](ABC):
    """Facade selecting compatible serializers and deserializers explicitly."""

    @abstractmethod
    def serializer(
        self,
        serializer_id: str,
        /,
    ) -> DataObjectSerializer[ObjectT, ModelT]:
        """Return the explicitly identified serializer."""

    @abstractmethod
    def deserializer(
        self,
        deserializer_id: str,
        /,
    ) -> DataObjectDeserializer[ModelT, ObjectT]:
        """Return the explicitly identified deserializer."""


class DataObjectValidator[
    RequestT: DataObjectRequest,
    ResultT: DataObjectResult,
](DataObjectActionizer[RequestT, ResultT], ABC):
    """Runtime-enforced actionizer role for validation."""


class DataObjectVerifier[
    RequestT: DataObjectRequest,
    ResultT: DataObjectResult,
](DataObjectActionizer[RequestT, ResultT], ABC):
    """Runtime-enforced actionizer role for verification."""


class DataObjectUncertaintyQualification[
    RequestT: DataObjectRequest,
    ResultT: DataObjectResult,
](DataObjectActionizer[RequestT, ResultT], ABC):
    """Runtime-enforced actionizer role for uncertainty qualification."""


__all__ = [
    "DataObject",
    "DataObjectActionizer",
    "DataObjectCodex",
    "DataObjectDeserializer",
    "DataObjectModel",
    "DataObjectRequest",
    "DataObjectResult",
    "DataObjectSerializer",
    "DataObjectUncertaintyQualification",
    "DataObjectValidator",
    "DataObjectVerifier",
]
