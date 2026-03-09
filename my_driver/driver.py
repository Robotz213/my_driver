# ruff: noqa: D100, D101, D107, SLF001
from __future__ import annotations

import platform
import shutil
from collections.abc import Iterable, Sequence
from contextlib import suppress
from pathlib import Path
from tempfile import mkdtemp
from threading import Event
from types import CellType
from typing import (
    TYPE_CHECKING,
    Literal,
    TypedDict,
    Unpack,
    cast,
    override,
)
from zipfile import ZipFile

from selenium.common import NoSuchElementException
from selenium.webdriver import Chrome as SeChromeDriver
from selenium.webdriver.chrome.options import Options as SeChromeOptions
from selenium.webdriver.support.wait import (
    WebDriverWait as SEWebDriverWait,
)
from seleniumwire.webdriver import Chrome as SWireChrome

from .constants import ARGUMENTS, PREFERENCES, SETTINGS, Preferences
from .web_element import WebElement

if TYPE_CHECKING:
    from collections.abc import Callable

    from selenium.webdriver.chrome.service import Service
    from seleniumwire.request import Request

    from ._typing import Any, Bot, Driver
    from .constants import Preferences


type Exc = Iterable[type[Exception]]
type ExperimentalOptions = str | int | dict[Any, Any] | list[str]


WORKDIR = Path.cwd()


POLL_FREQUENCY: float = 0.5


IGNORED_EXCEPTIONS: Exc = (NoSuchElementException,)


type ClosureType = tuple[CellType, ...]


class Options(SeChromeOptions):
    @override
    def add_experimental_option(
        self,
        name: str,
        value: Preferences,
    ) -> None:
        return super().add_experimental_option(name, value)


class ChromeDriverKwargs(TypedDict):
    options: Options | None
    service: Service | None


class SeleniumWireOptions(TypedDict):
    addr: str
    port: int
    exclude_hosts: Sequence[str]
    standalone: bool


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

    def __call__(self, *arg: P.args, **kwarg: P.kwargs) -> R:
        args = arg
        kwargs = kwarg.copy()

        predicate: Callable[P, R] = cast("Callable[P, R]", arg[0])
        if all((
            any((
                "presence" in predicate.__qualname__,
                "visibility" in predicate.__qualname__,
            )),
            not kwarg.get("message"),
        )):
            closure = cast("ClosureType", predicate.__closure__)
            element = closure[0].cell_contents[1]
            kwarg.update({
                "message": f'Elemento "{element}" não encontrado!',
            })

        return self._fn(*args, **kwargs)


class Chrome(SeChromeDriver):
    def __init__(
        self,
        options: Options | None = None,
        service: Service | None = None,
        *,
        keep_alive: bool = True,
    ) -> None:
        self._event_driver = Event()
        super().__init__(options, service, keep_alive)

    def quit(self) -> None:
        self._event_driver.set()
        return super().quit()

    @property
    def is_closed(self) -> bool:
        return self._event_driver.is_set()

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
        self._event_driver = Event()
        super().__init__(
            seleniumwire_options=seleniumwire_options,  # pyright: ignore[reportCallIssue]
            **kwargs,
        )  # pyright: ignore[reportCallIssue]

    def quit(self) -> None:
        self._event_driver.set()
        return super().quit()

    @property
    def is_closed(self) -> bool:
        return self._event_driver.is_set()


class BotDriver:
    """Gerenciador do webdriver para a execução dos bots."""

    _wait: WebDriverWait[Driver]

    def exit(self) -> None:

        with suppress(Exception):
            self.driver.delete_all_cookies()

        with suppress(Exception):
            self.driver.quit()

    @property
    def wait(self) -> WebDriverWait[Driver]:
        return self._wait

    @wait.setter
    def wait(self, v: WebDriverWait[Driver]) -> None:
        self._wait = v

    def __init__[T](self, bot: Bot) -> None:
        options = Options()
        user_data_dir = WORKDIR.joinpath("chrome-data", bot.id_execucao)

        if user_data_dir.exists():
            shutil.rmtree(path=user_data_dir, ignore_errors=True)

        user_data_dir.mkdir(parents=True)
        user_data_dir.chmod(0o775)

        options.add_argument(f"--user-data-dir={user_data_dir!s}")

        for argument in ARGUMENTS:
            options.add_argument(argument)

        if platform.system() != "Windows":
            options.add_argument("--no-sandbox")

        download_dir = str(bot.output_dir_path)
        preferences = PREFERENCES

        preferences.update({
            "download.default_directory": download_dir,
        })
        preferences.update({
            "printing.print_preview_sticky_settings.appState": SETTINGS,
        })

        options.add_experimental_option(name="prefs", value=preferences)
        ext_pathtemp = Path(mkdtemp())

        for root, _, files in WORKDIR.joinpath(
            "chrome-extensions",
        ).walk():
            for file in filter(lambda x: x.endswith(".zip"), files):
                filepath = root.joinpath(file)
                extracted_filepath = ext_pathtemp.joinpath(
                    file.removesuffix(".zip"),
                )
                with ZipFile(filepath) as zipfile:
                    zipfile.extractall(extracted_filepath)

                str_filep = str(extracted_filepath)
                options.add_argument(f"--load-extension={str_filep}")

        if bot.config.get("sistema").upper() != "PJE":
            self.driver = cast("Driver", Chrome(options=options))

        elif bot.config.get("sistema").upper() == "PJE":
            self.driver = cast("Driver", SeWireChrome(options=options))

        self.driver._web_element_cls = WebElement  # pyright: ignore[reportPrivateUsage]
        self.wait = WebDriverWait(self.driver, 10)

        self.wait.until = WrapperDriverWait(self.wait.until)

        self.driver.maximize_window()
