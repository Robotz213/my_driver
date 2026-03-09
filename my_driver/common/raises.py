# ruff: noqa: D103, D100

from __future__ import annotations

from typing import NoReturn

from .exceptions import FatalError


def raise_execution_error(
    message: str,
    exc: Exception | None = None,
) -> NoReturn:

    raise FatalError(message=message) from exc
