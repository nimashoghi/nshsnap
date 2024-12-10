from __future__ import annotations

__codegen__ = True

from nshsnap.cli import SnapshotConfig as SnapshotConfig

from .SnapshotConfig_typed_dict import CreateSnapshotConfig as CreateSnapshotConfig
from .SnapshotConfig_typed_dict import (
    SnapshotConfigTypedDict as SnapshotConfigTypedDict,
)

SnapshotConfigInstanceOrDict = SnapshotConfig | SnapshotConfigTypedDict


__all__ = [
    "CreateSnapshotConfig",
    "SnapshotConfig",
    "SnapshotConfigInstanceOrDict",
    "SnapshotConfigTypedDict",
]
