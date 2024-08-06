import logging
from pathlib import Path
from typing import Any, Literal

import nshconfig as C
from typing_extensions import TypedDict, assert_never

from ._pip_deps import EditablePackageDependency, current_pip_dependencies
from ._util import _gitignored_dir, snapshot_id

log = logging.getLogger(__name__)


class SnapshotConfigKwargsDict(TypedDict, total=False):
    snapshot_dir: Path
    """The directory to save snapshots to."""

    modules: list[str]
    """Modules to snapshot. Default: `[]`."""

    editable_modules: bool
    """Snapshot all editable modules. Default: `False`."""

    on_module_not_found: Literal["raise", "warn"]
    """What to do when a module is not found. Default: `"warn"`."""


SNAPSHOT_CONFIG_DEFAULT: SnapshotConfigKwargsDict = {
    "editable_modules": False,
    "on_module_not_found": "warn",
}


def _default_snapshot_dir() -> Path:
    snaps_folder = Path.home() / ".cache" / "nshsnap" / "snapshots"
    snaps_folder.mkdir(parents=True, exist_ok=True)

    return _gitignored_dir(snaps_folder / snapshot_id(), create=True)


def _editable_modules(on_module_not_found: Literal["raise", "warn"]):
    for dep in current_pip_dependencies():
        if not isinstance(dep, EditablePackageDependency):
            continue

        if (module_name := dep.importable_module_name()) is None:
            msg = (
                f"Could not find an importable module name for editable package {dep.name}. "
                "Please double-check to make sure that the package is installed correctly. "
                "Delete any existing *.egg-info directories in the package's source directory, "
                "pip uninstall the package, and then reinstall it."
            )
            match on_module_not_found:
                case "raise":
                    raise ValueError(msg)
                case "warn":
                    log.warning(msg)
                    continue
                case _:
                    assert_never(on_module_not_found)

        yield module_name


class SnapshotConfig(C.Config):
    snapshot_dir: Path = C.Field(default_factory=_default_snapshot_dir)
    """The directory to save snapshots to."""

    modules: list[str] = []
    """Modules to snapshot. Default: `[]`."""

    on_module_not_found: Literal["raise", "warn"] = "warn"
    """What to do when a module is not found. Default: `"warn"`."""

    @classmethod
    def from_kwargs(cls, kwargs: SnapshotConfigKwargsDict):
        kwargs = {**SNAPSHOT_CONFIG_DEFAULT, **kwargs}
        if kwargs.pop("editable_modules"):
            kwargs["modules"] = sorted(
                list(
                    set(kwargs.get("modules", [])).union(
                        _editable_modules(kwargs.get("on_module_not_found", "warn"))
                    )
                ),
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
        on_module_not_found: Literal["raise", "warn"] = "warn",
    ):
        kwargs: dict[str, Any] = {}
        if snapshot_dir is not None:
            kwargs["snapshot_dir"] = snapshot_dir
        kwargs["modules"] = sorted(
            list(set(additional_modules).union(_editable_modules(on_module_not_found))),
            key=str.casefold,
        )
        return cls(**kwargs)
