from __future__ import annotations

import typing_extensions as typ

if typ.TYPE_CHECKING:
    from nshsnap._pip_deps import RegularPackageDependency


__codegen__ = True


# Schema entries
class RegularPackageDependencyTypedDict(typ.TypedDict, total=False):
    name: typ.Required[str]

    version: str | None

    type: str


@typ.overload
def CreateRegularPackageDependency(
    **dict: typ.Unpack[RegularPackageDependencyTypedDict],
) -> RegularPackageDependency: ...


@typ.overload
def CreateRegularPackageDependency(
    data: RegularPackageDependencyTypedDict | RegularPackageDependency, /
) -> RegularPackageDependency: ...


def CreateRegularPackageDependency(*args, **kwargs):
    from nshsnap._pip_deps import RegularPackageDependency

    if not args and kwargs:
        # Called with keyword arguments
        return RegularPackageDependency.from_dict(kwargs)
    elif len(args) == 1:
        return RegularPackageDependency.from_dict_or_instance(args[0])
    else:
        raise TypeError(
            f"CreateRegularPackageDependency accepts either a RegularPackageDependencyTypedDict, "
            f"keyword arguments, or a RegularPackageDependency instance"
        )
