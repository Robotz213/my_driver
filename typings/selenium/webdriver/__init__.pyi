from collections.abc import Sequence
from typing import TypedDict

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import ByType

from backend.resources.driver import WebElement

class Cookie(TypedDict):
    domain: str
    expiry: int
    httpOnly: bool
    name: str
    path: str
    sameSite: str
    secure: int
    value: str

class RelativeBy:
    type LocatorType = dict[ByType, str]

    def __init__(
        self,
        root: dict[ByType, str] | None = None,
        filters: list | None = None,
    ) -> None: ...

class Chrome(WebDriver):
    @property
    def is_closed(self) -> bool: ...
    def get_cookies(self) -> list[Cookie]: ...  # pyright: ignore[reportIncompatibleMethodOverride]
    def execute_script[T, P](self, script: str, *args: P) -> T: ...
    def find_element(
        self,
        by: RelativeBy,
        value: str,
    ) -> WebElement: ...
    def find_elements(
        self,
        by: RelativeBy,
        value: str,
    ) -> Sequence[WebElement]: ...
