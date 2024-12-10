from __future__ import annotations

__codegen__ = True

from nshsnap._meta import SnapshotConfig as SnapshotConfig
from nshsnap._meta import SnapshotMetadata as SnapshotMetadata

from .SnapshotConfig_typed_dict import CreateSnapshotConfig as CreateSnapshotConfig
from .SnapshotConfig_typed_dict import (
    SnapshotConfigTypedDict as SnapshotConfigTypedDict,
)

SnapshotConfigInstanceOrDict = SnapshotConfig | SnapshotConfigTypedDict

from .SnapshotMetadata_typed_dict import (
    CreateSnapshotMetadata as CreateSnapshotMetadata,
)
from .SnapshotMetadata_typed_dict import (
    SnapshotMetadataTypedDict as SnapshotMetadataTypedDict,
)

SnapshotMetadataInstanceOrDict = SnapshotMetadata | SnapshotMetadataTypedDict


__all__ = [
    "CreateSnapshotConfig",
    "CreateSnapshotMetadata",
    "SnapshotConfig",
    "SnapshotConfigInstanceOrDict",
    "SnapshotConfigTypedDict",
    "SnapshotMetadata",
    "SnapshotMetadataInstanceOrDict",
    "SnapshotMetadataTypedDict",
]
