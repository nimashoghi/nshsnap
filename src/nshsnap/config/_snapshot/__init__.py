from __future__ import annotations

__codegen__ = True

from typing import TYPE_CHECKING

# Config/alias imports

if TYPE_CHECKING:
    from nshsnap._snapshot import SnapshotConfig as SnapshotConfig
    from nshsnap._snapshot import SnapshotMetadata as SnapshotMetadata
else:

    def __getattr__(name):
        import importlib

        if name in globals():
            return globals()[name]
        if name == "SnapshotConfig":
            return importlib.import_module("nshsnap._snapshot").SnapshotConfig
        if name == "SnapshotMetadata":
            return importlib.import_module("nshsnap._snapshot").SnapshotMetadata
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Submodule exports
