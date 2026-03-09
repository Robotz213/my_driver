from __future__ import annotations

from types import CellType

type Any = object
type ClosureType = tuple[CellType, ...]


__all__ = ["Any", "ClosureType"]
