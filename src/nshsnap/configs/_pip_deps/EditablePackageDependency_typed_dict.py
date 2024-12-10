from __future__ import annotations

import typing_extensions as typ

if typ.TYPE_CHECKING:
    from nshsnap._pip_deps import EditablePackageDependency


__codegen__ = True


# Schema entries
class EditablePackageDependencyTypedDict(typ.TypedDict, total=False):
    name: typ.Required[str]

    version: str | None

    type: str

    editable_project_location: typ.Required[str]


@typ.overload
def CreateEditablePackageDependency(
    **dict: typ.Unpack[EditablePackageDependencyTypedDict],
) -> EditablePackageDependency: ...


@typ.overload
def CreateEditablePackageDependency(
    data: EditablePackageDependencyTypedDict | EditablePackageDependency, /
) -> EditablePackageDependency: ...


def CreateEditablePackageDependency(*args, **kwargs):
    from nshsnap._pip_deps import EditablePackageDependency

    if not args and kwargs:
        # Called with keyword arguments
        return EditablePackageDependency.from_dict(kwargs)
    elif len(args) == 1:
        return EditablePackageDependency.from_dict_or_instance(args[0])
    else:
        raise TypeError(
            f"CreateEditablePackageDependency accepts either a EditablePackageDependencyTypedDict, "
            f"keyword arguments, or a EditablePackageDependency instance"
        )
