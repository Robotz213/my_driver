# ruff: noqa: D100, D101, D107, SLF001
from __future__ import annotations

import platform
import shutil
from collections.abc import Iterable
from contextlib import suppress
from pathlib import Path
from tempfile import mkdtemp
from typing import TYPE_CHECKING, cast
from zipfile import ZipFile

from selenium.webdriver.chrome.options import Options

from ._driver import Chrome, SeWireChrome
from ._driver_wait import WebDriverWait, WrapperDriverWait
from .constants import ARGUMENTS, PREFERENCES, SETTINGS, WORKDIR
from .web_element import WebElement

if TYPE_CHECKING:
    from ._typing import Any, Bot, Driver


type Exc = Iterable[type[Exception]]
type ExperimentalOptions = str | int | dict[Any, Any] | list[str]


class BotDriver:
    __wait: WebDriverWait[Driver]

    def exit(self) -> None:

        with suppress(Exception):
            self.driver.delete_all_cookies()

        with suppress(Exception):
            self.driver.quit()

    @property
    def wait(self) -> WebDriverWait[Driver]:
        return self.__wait

    @wait.setter
    def wait(self, v: WebDriverWait[Driver]) -> None:
        self.__wait = v

    def __init__(self, bot: Bot) -> None:
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
        preferences = cast("dict", PREFERENCES)

        preferences.update({
            "download.default_directory": download_dir,
        })
        preferences.update({
            "printing.print_preview_sticky_settings.appState": SETTINGS,
        })

        options.add_experimental_option(name="prefs", value=preferences)
        ext_pathtemp = Path(mkdtemp())

        extensions = WORKDIR.joinpath("chrome-extensions")

        for root, _, files in extensions.walk():
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

        self.driver._web_element_cls = WebElement
        self.wait = WebDriverWait(self.driver, 10)

        self.wait.until = WrapperDriverWait(self.wait.until)

        self.driver.maximize_window()
