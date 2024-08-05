import logging
from pathlib import Path
from typing import Any

import nshconfig as C
from typing_extensions import TypedDict

from ._pip_deps import EditablePackageDependency, current_pip_dependencies
from ._util import _gitignored_dir, snapshot_id

log = logging.getLogger(__name__)


class SnapshotConfigKwargsDict(TypedDict, total=False):
    snapshot_dir: Path
    """The directory to save snapshots to."""

    modules: list[str]
    """Modules to snapshot. Default: `[]`."""

    editable_modules: bool
    """Snapshot all editable modules. Default: `True`."""


SNAPSHOT_CONFIG_DEFAULT: SnapshotConfigKwargsDict = {
    "editable_modules": True,
}


def _default_snapshot_dir() -> Path:
    snaps_folder = Path.home() / ".cache" / "nshsnap" / "snapshots"
    snaps_folder.mkdir(parents=True, exist_ok=True)

    return _gitignored_dir(snaps_folder / snapshot_id(), create=True)


def _editable_modules():
    for dep in current_pip_dependencies():
        if not isinstance(dep, EditablePackageDependency):
            continue
        yield dep.name


class SnapshotConfig(C.Config):
    snapshot_dir: Path = C.Field(default_factory=_default_snapshot_dir)
    """The directory to save snapshots to."""

    modules: list[str] = []
    """Modules to snapshot. Default: `[]`."""

    @classmethod
    def from_kwargs(cls, kwargs: SnapshotConfigKwargsDict):
        kwargs = {**SNAPSHOT_CONFIG_DEFAULT, **kwargs}
        if kwargs.pop("editable_modules"):
            pass

        kwargs["modules"] = sorted(
            list(set(kwargs.get("modules", [])).union(_editable_modules())),
            key=str.casefold,
        )
        return cls(
            **kwargs,  # pyright: ignore[reportCallIssue]
        )

    @classmethod
    def from_editable_modules(
        cls,
        *,
        snapshot_dir: Path | None = None,
        additional_modules: list[str] = [],
    ):
        kwargs: dict[str, Any] = {}
        if snapshot_dir is not None:
            kwargs["snapshot_dir"] = snapshot_dir
        kwargs["modules"] = sorted(
            list(set(additional_modules).union(_editable_modules())),
            key=str.casefold,
        )
        return cls(**kwargs)
