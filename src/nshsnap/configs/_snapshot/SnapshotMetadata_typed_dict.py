from __future__ import annotations

import typing_extensions as typ

if typ.TYPE_CHECKING:
    from nshsnap._meta import SnapshotMetadata


__codegen__ = True

# Definitions


class EditablePackageDependency(typ.TypedDict, total=False):
    name: typ.Required[str]

    version: str | None

    type: str

    editable_project_location: typ.Required[str]


class RegularPackageDependency(typ.TypedDict, total=False):
    name: typ.Required[str]

    version: str | None

    type: str


class SnapshotConfig(typ.TypedDict, total=False):
    snapshot_dir: str | None
    """The directory to save snapshots to."""

    modules: list[str]
    """Modules to snapshot. Default: `[]`."""

    on_module_not_found: typ.Literal["raise"] | typ.Literal["warn"]
    """What to do when a module is not found. Default: `"warn"`."""

    editable_modules: bool
    """Snapshot all editable modules. Default: `True`."""


# Schema entries
class SnapshotMetadataTypedDict(typ.TypedDict):
    config: SnapshotConfig
    """The configuration for the snapshot."""

    timestamp: str
    """The timestamp of the snapshot."""

    pip_dependencies: list[RegularPackageDependency | EditablePackageDependency] | None
    """The parsed dependencies from the output of `pip list --format=json`."""


@typ.overload
def CreateSnapshotMetadata(
    **dict: typ.Unpack[SnapshotMetadataTypedDict],
) -> SnapshotMetadata: ...


@typ.overload
def CreateSnapshotMetadata(
    data: SnapshotMetadataTypedDict | SnapshotMetadata, /
) -> SnapshotMetadata: ...


def CreateSnapshotMetadata(*args, **kwargs):
    from nshsnap._meta import SnapshotMetadata

    if not args and kwargs:
        # Called with keyword arguments
        return SnapshotMetadata.from_dict(kwargs)
    elif len(args) == 1:
        return SnapshotMetadata.from_dict_or_instance(args[0])
    else:
        raise TypeError(
            f"CreateSnapshotMetadata accepts either a SnapshotMetadataTypedDict, "
            f"keyword arguments, or a SnapshotMetadata instance"
        )
