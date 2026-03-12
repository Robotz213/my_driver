"""Gerenciador do webdriver para a execução dos bots."""

from my_driver import hook

from ._driver_wait import WebDriverWait
from .main import BotDriver
from .web_element import WebElement

__all__ = ["BotDriver", "WebDriverWait", "WebElement", "hook"]
