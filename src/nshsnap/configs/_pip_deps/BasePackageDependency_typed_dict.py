from __future__ import annotations

import typing_extensions as typ

if typ.TYPE_CHECKING:
    from nshsnap._pip_deps import BasePackageDependency


__codegen__ = True


# Schema entries
class BasePackageDependencyTypedDict(typ.TypedDict, total=False):
    name: typ.Required[str]

    version: str | None


@typ.overload
def CreateBasePackageDependency(
    **dict: typ.Unpack[BasePackageDependencyTypedDict],
) -> BasePackageDependency: ...


@typ.overload
def CreateBasePackageDependency(
    data: BasePackageDependencyTypedDict | BasePackageDependency, /
) -> BasePackageDependency: ...


def CreateBasePackageDependency(*args, **kwargs):
    from nshsnap._pip_deps import BasePackageDependency

    if not args and kwargs:
        # Called with keyword arguments
        return BasePackageDependency.from_dict(kwargs)
    elif len(args) == 1:
        return BasePackageDependency.from_dict_or_instance(args[0])
    else:
        raise TypeError(
            f"CreateBasePackageDependency accepts either a BasePackageDependencyTypedDict, "
            f"keyword arguments, or a BasePackageDependency instance"
        )
