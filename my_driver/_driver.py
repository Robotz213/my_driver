from __future__ import annotations

from threading import Event
from typing import (
    TYPE_CHECKING,
    NotRequired,
    TypedDict,
    Unpack,
    cast,
)

from selenium.webdriver import Chrome as SeChromeDriver
from seleniumwire.webdriver import Chrome as SWireChrome

if TYPE_CHECKING:
    from collections.abc import Sequence

    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from seleniumwire.request import Request

    from ._typing import Any


class ChromeDriverKwargs(TypedDict):
    options: NotRequired[Options]
    service: NotRequired[Service]


class SeleniumWireOptions(TypedDict):
    addr: str
    port: int
    exclude_hosts: Sequence[str]
    standalone: bool


class Chrome(SeChromeDriver):
    def __init__(
        self,
        options: Options | None = None,
        service: Service | None = None,
        *,
        keep_alive: bool = True,
    ) -> None:
        self.__event_driver = Event()
        super().__init__(options, service, keep_alive)

    def quit(self) -> None:
        self.__event_driver.set()
        return super().quit()

    @property
    def is_closed(self) -> bool:
        return self.__event_driver.is_set()

    @property
    def requests(self) -> list[Request]:
        raise NotImplementedError


class SeWireChrome(SWireChrome):
    def __init__(
        self,
        *,
        seleniumwire_options: SeleniumWireOptions | None = None,
        **kwargs: Unpack[ChromeDriverKwargs],
    ) -> None:
        self.__event_driver = Event()
        super().__init__(
            seleniumwire_options=cast(
                "dict[str, Any]",
                seleniumwire_options,
            ),
        )

    def quit(self) -> None:
        self.__event_driver.set()
        return super().quit()

    @property
    def is_closed(self) -> bool:
        return self.__event_driver.is_set()
