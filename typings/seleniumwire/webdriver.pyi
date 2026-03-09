from typing import TypedDict

from selenium.webdriver import Chrome as _Chrome
from seleniumwire.inspect import InspectRequestsMixin

from backend._typing import Any

class Cookie(TypedDict):
    domain: str
    expiry: int
    httpOnly: bool
    name: str
    path: str
    sameSite: str
    secure: int
    value: str

class DriverCommonMixin:
    def _setup_backend(
        self,
        seleniumwire_options: dict[str, Any],
    ) -> dict[str, Any]: ...
    @property
    def proxy(self) -> dict[str, Any]: ...
    @proxy.setter
    def proxy(self, proxy_conf: dict[str, Any]) -> None: ...

class Chrome(InspectRequestsMixin, DriverCommonMixin, _Chrome):
    def __init__(
        self,
        *args: Any,
        seleniumwire_options: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None: ...
    @property
    def is_closed(self) -> bool: ...
    def get_cookies(self) -> list[Cookie]: ...
