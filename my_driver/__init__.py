"""Gerenciador do webdriver para a execução dos bots."""

from .driver import BotDriver, WebDriverWait
from .web_element import WebElement

__all__ = ["BotDriver", "WebDriverWait", "WebElement"]
