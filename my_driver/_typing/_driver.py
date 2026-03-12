from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from selenium.webdriver.chrome.webdriver import WebDriver as SeChrome
from seleniumwire.webdriver import Chrome as WiredChrome

if TYPE_CHECKING:
    from ._types import Any


type Exc = Iterable[type[Exception]]
type ExperimentalOptions = str | int | dict[Any, Any] | list[str]


class Driver(WiredChrome, SeChrome):
    @property
    def is_closed(self) -> bool: ...


__all__ = ["Driver", "Exc", "ExperimentalOptions"]
