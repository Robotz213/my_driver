from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from my_driver._typing import Any


class FatalError(Exception):
    """Exceção fatal na execução do Driver."""

    message: ClassVar[str] = "Fatal error in Driver execution."

    def __init__(
        self,
        *args: Any,
        message: str | None = None,
    ) -> None:
        Exception.__init__(self, message)
