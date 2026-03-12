# ruff: noqa: D100, B010, D103

from __future__ import annotations

import sys
from importlib import invalidate_caches
from importlib.abc import MetaPathFinder, SourceLoader
from importlib.util import spec_from_loader
from pathlib import Path
from types import MethodType
from typing import TYPE_CHECKING
from weakref import WeakMethod, ref

from packaging.version import parse

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec

    from my_driver._typing import Any


WORKDIR = Path.cwd()


class Legacy(SourceLoader):
    def get_data(self, path: str) -> str:
        return Path(path).read_text("utf-8")

    def get_filename(self, fullname: str) -> str:
        return fullname

    def exec_module(self, module: ModuleSpec) -> None:
        setattr(module, "_saferef", self.safe_ref)
        setattr(module, "parse_version", parse)

    def safe_ref(self, target: Any) -> Any:
        if isinstance(target, MethodType):
            return WeakMethod(target)

        return ref(target)


class BlinkerPatch(MetaPathFinder):
    def find_spec(
        self,
        fullname: str,
        _path: str,
        _target: Any = None,
    ) -> ModuleSpec | None:
        if fullname == "blinker._saferef":
            return spec_from_loader(fullname, loader=Legacy())

        if fullname.startswith("pkg_resources"):
            return spec_from_loader(fullname, loader=Legacy())

        return None


def patch_modules() -> None:
    sys.meta_path.insert(0, BlinkerPatch())
    invalidate_caches()


patch_modules()
__all__ = ["patch_modules"]
