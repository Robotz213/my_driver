# ruff: noqa: D100, D107, D101
from __future__ import annotations

import platform
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, Self, TypedDict, cast

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.utils import keys_to_typing
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webelement import (
    WebElement as SEWebElement,
)
from selenium.webdriver.support.ui import Select

from .common.raises import raise_execution_error
from .constants import (
    COMMAND_EXTRACT_XPATH,
    COMMAND_SELECT2,
    GET_INNER_TEXT,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ._typing import Any, Driver


class RectWebElement(TypedDict):
    height: float
    width: float
    x: float
    y: float


class WebElement(SEWebElement):
    @property
    def parent(self) -> Driver:
        return self._parent

    @parent.setter
    def parent(self, val: Driver) -> None:
        self._parent = val

    @property
    def actions(self) -> ActionChains:
        return self._actions

    @actions.setter
    def actions(self, val: ActionChains) -> None:
        self._actions = val

    def __init__(self, parent: Driver, id_: str) -> None:
        self.actions = ActionChains(parent)
        self.current_driver = parent

        super().__init__(parent, id_)

    def execute_script(
        self,
        script: str,
        *args: object,
    ) -> object:

        return self.parent.execute_script(script, self, *args)

    def __call__(self, *args: Any, **kwargs: Any) -> None:

        return super().click()

    @property
    def rect(self) -> dict[str, str]:

        return super().rect

    @property
    def location(self) -> dict[str, str]:

        return super().location

    @property
    def current_driver(self) -> Driver:

        return self._current_driver

    @current_driver.setter
    def current_driver(self, val: Driver) -> None:
        self._current_driver = val

    def double_click(self) -> None:
        """Execute um duplo clique no elemento web."""
        self.actions.double_click(self).perform()

    def selecionar_item(self, item: str) -> None:

        items = self.find_elements(By.TAG_NAME, "option")
        opt_itens: dict[str, str] = {}

        for it in items:
            key: str = self.parent.execute_script(GET_INNER_TEXT, it)
            value = it.get_attribute("value")
            if value:
                opt_itens.update({key.upper(): value})

        opt = opt_itens.get(item.upper())
        if not opt:
            raise_execution_error(
                message=f'Opção "{item}" não encontrada!',
            )

        return Select(self).select_by_value(opt)

    def select_item(self, item: str) -> None:
        return Select(self).select_by_value(item)

    def click(self) -> None:
        sleep(0.05)

        try:
            super().click()

        except ElementClickInterceptedException as e:
            element_xpath = self.execute_script(
                COMMAND_EXTRACT_XPATH,
                self,
            )
            message = f"Elemento não clicável: {element_xpath}"
            raise ElementClickInterceptedException(msg=message) from e

        sleep(0.05)

    def clear(self) -> None:

        self.click()
        sleep(0.5)
        super().clear()
        sleep(1)

    def scroll_to(self) -> None:
        self.actions.scroll_to_element(self)
        sleep(0.5)

    def find_element(
        self,
        by: str = By.ID,
        value: str | None = None,
    ) -> WebElement:
        return cast(
            "WebElement",
            super().find_element(by=by, value=value),
        )

    def find_elements(
        self,
        by: str = By.ID,
        value: str | None = None,
    ) -> Sequence[WebElement]:
        return cast(
            "Sequence[WebElement]",
            super().find_elements(by=by, value=value),
        )

    def send_keys(self, *value: str) -> None:
        word = value
        if isinstance(value, (tuple, str)):
            word = value[0]

        send = False

        if_keys = list(
            filter(
                lambda key: str(getattr(Keys, key)) == word,
                dir(Keys),
            ),
        )

        if if_keys:
            send = True
            super().send_keys(word)
            return

        if not send:
            for c in str(word):
                sleep(0.01)
                super().send_keys(c)

    def send_text(self, text: str) -> None:

        super().send_keys(text)

    def send_file(self, file: str | Path) -> None:
        file_ = file
        if isinstance(file, Path):
            file_ = (
                file.as_posix()
                if platform.system() == "Linux"
                else str(file)
            )
        self._execute(
            Command.SEND_KEYS_TO_ELEMENT,
            {
                "text": "".join(keys_to_typing(str(file_))),
                "value": keys_to_typing(str(file_)),
            },
        )

    def display_none(self) -> None:
        while True:
            style = str(self.get_attribute("style"))
            if "display: none;" not in style:
                sleep(0.01)
                break

    def select2(self, opcao: str) -> None:
        items = self.find_elements(By.TAG_NAME, "option")
        opt_itens: dict[str, str] = {}

        for item in items:
            value_item = item.get_attribute("value") or ""
            command = "return $(arguments[0]).text();"
            text_item = self.parent.execute_script(command, item)
            text_item = " ".join([
                item
                for item in str(text_item).strip().split(" ")
                if item
            ]).upper()
            opt_itens.update({text_item: value_item})

        to_search = " ".join(opcao.split(" ")).upper()
        value_opt = opt_itens.get(to_search)

        if value_opt:
            self.parent.execute_script(
                COMMAND_SELECT2,
                self,
                value_opt,
            )
            return

        raise_execution_error(
            message=f'Opção "{to_search}" não encontrada!',
        )

    def scroll_from_origin(
        self,
        delta_x: int,
        delta_y: int,
        origin: Self | None = None,
    ) -> None:

        if not origin:
            origin = self

        location = origin.location
        scroll_origin = ScrollOrigin.from_element(
            origin,
            x_offset=int(location.get("x") or "0"),
            y_offset=int(location.get("y") or "0"),
        )

        self.actions.scroll_to_element(self)

        with suppress(Exception):
            return self.actions.scroll_from_origin(
                scroll_origin=scroll_origin,
                delta_x=0,
                delta_y=delta_y,
            ).perform()

    def scroll_to_element(self) -> None:

        self.actions.scroll_to_element(self).perform()

    def blur(self) -> None:

        command = "arguments[0].blur();"
        self.parent.execute_script(command, self)
