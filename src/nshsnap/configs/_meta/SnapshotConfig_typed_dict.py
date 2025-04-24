from __future__ import annotations

import typing_extensions as typ

if typ.TYPE_CHECKING:
    from nshsnap._config import SnapshotConfig


__codegen__ = True


# Schema entries
class SnapshotConfigTypedDict(typ.TypedDict, total=False):
    snapshot_dir: str | None
    """The directory to save snapshots to."""

    modules: list[str]
    """Modules to snapshot. Default: `[]`."""

    on_module_not_found: typ.Literal["raise"] | typ.Literal["warn"]
    """What to do when a module is not found. Default: `"warn"`."""

    editable_modules: bool
    """Snapshot all editable modules. Default: `True`."""


@typ.overload
def CreateSnapshotConfig(
    **dict: typ.Unpack[SnapshotConfigTypedDict],
) -> SnapshotConfig: ...


@typ.overload
def CreateSnapshotConfig(
    data: SnapshotConfigTypedDict | SnapshotConfig, /
) -> SnapshotConfig: ...


def CreateSnapshotConfig(*args, **kwargs):
    from nshsnap._config import SnapshotConfig

    if not args and kwargs:
        # Called with keyword arguments
        return SnapshotConfig.from_dict(kwargs)
    elif len(args) == 1:
        return SnapshotConfig.from_dict_or_instance(args[0])
    else:
        raise TypeError(
            f"CreateSnapshotConfig accepts either a SnapshotConfigTypedDict, "
            f"keyword arguments, or a SnapshotConfig instance"
        )
