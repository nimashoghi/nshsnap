from __future__ import annotations

__codegen__ = True

from nshsnap._pip_deps import BasePackageDependency as BasePackageDependency
from nshsnap._pip_deps import EditablePackageDependency as EditablePackageDependency
from nshsnap._pip_deps import PackageDependency as PackageDependency
from nshsnap._pip_deps import RegularPackageDependency as RegularPackageDependency

from .BasePackageDependency_typed_dict import (
    BasePackageDependencyTypedDict as BasePackageDependencyTypedDict,
)
from .BasePackageDependency_typed_dict import (
    CreateBasePackageDependency as CreateBasePackageDependency,
)

BasePackageDependencyInstanceOrDict = (
    BasePackageDependency | BasePackageDependencyTypedDict
)

from .EditablePackageDependency_typed_dict import (
    CreateEditablePackageDependency as CreateEditablePackageDependency,
)
from .EditablePackageDependency_typed_dict import (
    EditablePackageDependencyTypedDict as EditablePackageDependencyTypedDict,
)

EditablePackageDependencyInstanceOrDict = (
    EditablePackageDependency | EditablePackageDependencyTypedDict
)

from .RegularPackageDependency_typed_dict import (
    CreateRegularPackageDependency as CreateRegularPackageDependency,
)
from .RegularPackageDependency_typed_dict import (
    RegularPackageDependencyTypedDict as RegularPackageDependencyTypedDict,
)

RegularPackageDependencyInstanceOrDict = (
    RegularPackageDependency | RegularPackageDependencyTypedDict
)


__all__ = [
    "BasePackageDependency",
    "BasePackageDependencyInstanceOrDict",
    "BasePackageDependencyTypedDict",
    "CreateBasePackageDependency",
    "CreateEditablePackageDependency",
    "CreateRegularPackageDependency",
    "EditablePackageDependency",
    "EditablePackageDependencyInstanceOrDict",
    "EditablePackageDependencyTypedDict",
    "PackageDependency",
    "RegularPackageDependency",
    "RegularPackageDependencyInstanceOrDict",
    "RegularPackageDependencyTypedDict",
]
