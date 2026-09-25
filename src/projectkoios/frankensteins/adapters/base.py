"""Nominal base classes for maintained Project Koios adapters."""

from __future__ import annotations


class Adapter:
    """Common nominal base for maintained boundary adapters."""

    __slots__ = ()


class Binding(Adapter):
    """Nominal base for adapters to imported or deliberately vendored code."""

    __slots__ = ()


class Integration(Adapter):
    """Nominal base for adapters to external applications or services."""

    __slots__ = ()


__all__ = ["Adapter", "Binding", "Integration"]
