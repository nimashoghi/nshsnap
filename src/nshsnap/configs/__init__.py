from __future__ import annotations

__codegen__ = True

from nshsnap import SnapshotConfig as SnapshotConfig
from nshsnap._config import EditablePackageDependency as EditablePackageDependency
from nshsnap._meta import SnapshotMetadata as SnapshotMetadata
from nshsnap._pip_deps import BasePackageDependency as BasePackageDependency
from nshsnap._pip_deps import RegularPackageDependency as RegularPackageDependency

from ._pip_deps.BasePackageDependency_typed_dict import (
    BasePackageDependencyTypedDict as BasePackageDependencyTypedDict,
)
from ._pip_deps.BasePackageDependency_typed_dict import (
    CreateBasePackageDependency as CreateBasePackageDependency,
)

BasePackageDependencyInstanceOrDict = (
    BasePackageDependency | BasePackageDependencyTypedDict
)

from ._config.EditablePackageDependency_typed_dict import (
    CreateEditablePackageDependency as CreateEditablePackageDependency,
)
from ._config.EditablePackageDependency_typed_dict import (
    EditablePackageDependencyTypedDict as EditablePackageDependencyTypedDict,
)

EditablePackageDependencyInstanceOrDict = (
    EditablePackageDependency | EditablePackageDependencyTypedDict
)

from ._pip_deps.RegularPackageDependency_typed_dict import (
    CreateRegularPackageDependency as CreateRegularPackageDependency,
)
from ._pip_deps.RegularPackageDependency_typed_dict import (
    RegularPackageDependencyTypedDict as RegularPackageDependencyTypedDict,
)

RegularPackageDependencyInstanceOrDict = (
    RegularPackageDependency | RegularPackageDependencyTypedDict
)

from .SnapshotConfig_typed_dict import CreateSnapshotConfig as CreateSnapshotConfig
from .SnapshotConfig_typed_dict import (
    SnapshotConfigTypedDict as SnapshotConfigTypedDict,
)

SnapshotConfigInstanceOrDict = SnapshotConfig | SnapshotConfigTypedDict

from ._meta.SnapshotMetadata_typed_dict import (
    CreateSnapshotMetadata as CreateSnapshotMetadata,
)
from ._meta.SnapshotMetadata_typed_dict import (
    SnapshotMetadataTypedDict as SnapshotMetadataTypedDict,
)

SnapshotMetadataInstanceOrDict = SnapshotMetadata | SnapshotMetadataTypedDict


from . import _config as _config
from . import _meta as _meta
from . import _pip_deps as _pip_deps
from . import _snapshot as _snapshot
from . import cli as cli

__all__ = [
    "BasePackageDependency",
    "BasePackageDependencyInstanceOrDict",
    "BasePackageDependencyTypedDict",
    "CreateBasePackageDependency",
    "CreateEditablePackageDependency",
    "CreateRegularPackageDependency",
    "CreateSnapshotConfig",
    "CreateSnapshotMetadata",
    "EditablePackageDependency",
    "EditablePackageDependencyInstanceOrDict",
    "EditablePackageDependencyTypedDict",
    "RegularPackageDependency",
    "RegularPackageDependencyInstanceOrDict",
    "RegularPackageDependencyTypedDict",
    "SnapshotConfig",
    "SnapshotConfigInstanceOrDict",
    "SnapshotConfigTypedDict",
    "SnapshotMetadata",
    "SnapshotMetadataInstanceOrDict",
    "SnapshotMetadataTypedDict",
    "_config",
    "_meta",
    "_pip_deps",
    "_snapshot",
    "cli",
]
