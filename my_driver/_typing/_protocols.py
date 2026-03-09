from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypedDict

if TYPE_CHECKING:
    from pathlib import Path


class Config(TypedDict):
    sistema: str


class Bot(Protocol):
    @property
    def output_dir_path(self) -> Path: ...
    @property
    def id_execucao(self) -> str: ...
    @property
    def config(self) -> Config: ...
