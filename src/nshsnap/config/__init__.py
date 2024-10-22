from __future__ import annotations

__codegen__ = True

from typing import TYPE_CHECKING

# Config/alias imports

if TYPE_CHECKING:
    from nshsnap import SnapshotConfig as SnapshotConfig
    from nshsnap._config import EditablePackageDependency as EditablePackageDependency
    from nshsnap._meta import SnapshotMetadata as SnapshotMetadata
    from nshsnap._pip_deps import BasePackageDependency as BasePackageDependency
    from nshsnap._pip_deps import PackageDependency as PackageDependency
    from nshsnap._pip_deps import RegularPackageDependency as RegularPackageDependency
else:

    def __getattr__(name):
        import importlib

        if name in globals():
            return globals()[name]
        if name == "BasePackageDependency":
            return importlib.import_module("nshsnap._pip_deps").BasePackageDependency
        if name == "EditablePackageDependency":
            return importlib.import_module("nshsnap._config").EditablePackageDependency
        if name == "RegularPackageDependency":
            return importlib.import_module("nshsnap._pip_deps").RegularPackageDependency
        if name == "SnapshotConfig":
            return importlib.import_module("nshsnap").SnapshotConfig
        if name == "SnapshotMetadata":
            return importlib.import_module("nshsnap._meta").SnapshotMetadata
        if name == "PackageDependency":
            return importlib.import_module("nshsnap._pip_deps").PackageDependency
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Submodule exports
from . import _config as _config
from . import _meta as _meta
from . import _pip_deps as _pip_deps
from . import _snapshot as _snapshot
from . import cli as cli
