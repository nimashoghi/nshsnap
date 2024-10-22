from __future__ import annotations

__codegen__ = True

from typing import TYPE_CHECKING

# Config/alias imports

if TYPE_CHECKING:
    from nshsnap._config import EditablePackageDependency as EditablePackageDependency
    from nshsnap._config import SnapshotConfig as SnapshotConfig
else:

    def __getattr__(name):
        import importlib

        if name in globals():
            return globals()[name]
        if name == "EditablePackageDependency":
            return importlib.import_module("nshsnap._config").EditablePackageDependency
        if name == "SnapshotConfig":
            return importlib.import_module("nshsnap._config").SnapshotConfig
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Submodule exports
