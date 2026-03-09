from __future__ import annotations

from selenium.webdriver import Chrome as SeChrome
from seleniumwire.webdriver import Chrome as WiredChrome

type Any = object


class Driver(WiredChrome, SeChrome): ...


__all__ = ["Any", "Driver"]
