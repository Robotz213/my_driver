from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Literal,
    cast,
)

from selenium.common import TimeoutException
from selenium.webdriver.support.wait import (
    WebDriverWait as SEWebDriverWait,
)

from .constants import IGNORED_EXCEPTIONS, POLL_FREQUENCY

if TYPE_CHECKING:
    from collections.abc import Callable

    from ._typing import ClosureType, Exc


class WebDriverWait[D](SEWebDriverWait):
    def __init__(
        self,
        driver: D,
        timeout: float,
        poll_frequency: float = POLL_FREQUENCY,
        ignored_exceptions: Exc = IGNORED_EXCEPTIONS,
    ) -> None:
        super().__init__(
            driver,
            timeout,
            poll_frequency,
            ignored_exceptions,
        )

    def until[T](
        self,
        method: Callable[[D], Literal[False] | T],
        message: str = "Elemento não encontrado!",
    ) -> T:
        return super().until(method, message)


class WrapperDriverWait[**P, R]:
    def __init__(self, fn: Callable[P, R]) -> None:
        self._fn = fn

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:

        predicate: Callable[P, R] = cast("Callable[P, R]", args[0])
        message = "Elemento não encontrado!"
        if all((
            any((
                "presence" in predicate.__qualname__,
                "visibility" in predicate.__qualname__,
            )),
            not kwargs.get("message"),
        )):
            closure = cast("ClosureType", predicate.__closure__)
            element = closure[0].cell_contents[1]
            message = f'Elemento "{element}" não encontrado!'

        try:
            return self._fn(*args, **kwargs)

        except TimeoutException as e:
            raise TimeoutException(msg=message) from e
