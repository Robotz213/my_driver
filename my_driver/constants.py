# ruff: noqa: D100

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

from selenium.common.exceptions import NoSuchElementException

if TYPE_CHECKING:
    from ._typing import Exc, Preferences, Settings


WORKDIR = Path.cwd()
POLL_FREQUENCY: float = 0.5
IGNORED_EXCEPTIONS: Exc = (NoSuchElementException,)

SETTINGS: Settings = {
    "recentDestinations": [
        {"id": "Save as PDF", "origin": "local", "account": ""},
    ],
    "selectedDestinationId": "Save as PDF",
    "version": 2,
}


ARGUMENTS = [
    "--ignore-ssl-errors=yes",
    "--ignore-certificate-errors",
    "--display=:99",
    "--window-size=1360,768",
    "--kiosk-printing",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-software-rasterizer",
    "--disable-renderer-backgrounding",
    "--disable-backgrounding-occluded-windows",
    "--disable-blink-features=AutomationControlled",
    "--disable-features=MediaFoundationVideoCapture",
    "--disable-software-rasterizer",
    "--disable-features=VizDisplayCompositor",
]


PREFERENCES: Preferences = {
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True,
    "profile.default_content_settings.popups": 0,
    "printing.print_preview_sticky_settings.appState": cast(
        "Settings",
        {},
    ),
    "download.default_directory": "",
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.password_manager_leak_detection": False,
}


COMMAND_EXTRACT_XPATH = """
function getElementXPath(elt) {
    var path = "";
    for (; elt && elt.nodeType == 1; elt = elt.parentNode) {
        idx = Array.from(elt.parentNode.children).indexOf(elt) + 1;
        path = "/" + elt.tagName.toLowerCase() + "[" + idx + "]" + path;
    }
    return path;
}
return getElementXPath(arguments[0]);
"""

GET_INNER_TEXT = "return arguments[0].innerText"
COMMAND_SELECT2 = """
            const selector = $(arguments[0]);
            selector.val([arguments[1]]);
            selector.trigger("change");
            """
