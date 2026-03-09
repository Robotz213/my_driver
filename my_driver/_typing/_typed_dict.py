from typing import TypedDict


class RecentDestinations(TypedDict):
    id: str
    origin: str
    account: str


class Settings(TypedDict):
    recentDestinations: list[RecentDestinations]
    selectedDestinationId: str
    version: int


Preferences = TypedDict(
    "Preferences",
    {
        "download.prompt_for_download": bool,
        "plugins.always_open_pdf_externally": bool,
        "profile.default_content_settings.popups": int,
        "printing.print_preview_sticky_settings.appState": Settings,
        "download.default_directory": str,
        "credentials_enable_service": bool,
        "profile.password_manager_enabled": bool,
        "profile.password_manager_leak_detection": bool,
    },
)


__all__ = ["Preferences", "RecentDestinations", "Settings"]
