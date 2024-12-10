from __future__ import annotations

__codegen__ = True

from nshsnap._config import EditablePackageDependency as EditablePackageDependency
from nshsnap._config import SnapshotConfig as SnapshotConfig

from .EditablePackageDependency_typed_dict import (
    CreateEditablePackageDependency as CreateEditablePackageDependency,
)
from .EditablePackageDependency_typed_dict import (
    EditablePackageDependencyTypedDict as EditablePackageDependencyTypedDict,
)

EditablePackageDependencyInstanceOrDict = (
    EditablePackageDependency | EditablePackageDependencyTypedDict
)

from .SnapshotConfig_typed_dict import CreateSnapshotConfig as CreateSnapshotConfig
from .SnapshotConfig_typed_dict import (
    SnapshotConfigTypedDict as SnapshotConfigTypedDict,
)

SnapshotConfigInstanceOrDict = SnapshotConfig | SnapshotConfigTypedDict


__all__ = [
    "CreateEditablePackageDependency",
    "CreateSnapshotConfig",
    "EditablePackageDependency",
    "EditablePackageDependencyInstanceOrDict",
    "EditablePackageDependencyTypedDict",
    "SnapshotConfig",
    "SnapshotConfigInstanceOrDict",
    "SnapshotConfigTypedDict",
]
