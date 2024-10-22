from __future__ import annotations

__codegen__ = True

from typing import TYPE_CHECKING

# Config/alias imports

if TYPE_CHECKING:
    from nshsnap._pip_deps import BasePackageDependency as BasePackageDependency
    from nshsnap._pip_deps import EditablePackageDependency as EditablePackageDependency
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
            return importlib.import_module(
                "nshsnap._pip_deps"
            ).EditablePackageDependency
        if name == "RegularPackageDependency":
            return importlib.import_module("nshsnap._pip_deps").RegularPackageDependency
        if name == "PackageDependency":
            return importlib.import_module("nshsnap._pip_deps").PackageDependency
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Submodule exports
