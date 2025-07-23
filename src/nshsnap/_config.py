from __future__ import annotations

import copy
import logging
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Annotated, Any, Literal

import nshconfig as C
from typing_extensions import TypedDict, assert_never

from ._pip_deps import EditablePackageDependency, current_pip_dependencies
from ._util import _gitignored_dir, snapshot_id

log = logging.getLogger(__name__)


class SnapshotResolveModulesConfigKwargsDict(TypedDict, total=False):
    values: Iterable[Any]
    """Values to resolve modules from."""

    deep: Literal["deep", "deep-builtin", "shallow"]
    """How deep to resolve modules. Default: `"deep-builtin"`."""

    ignore_builtin: bool
    """Whether to ignore builtin modules when resolving modules. Default: `True`."""


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
            if on_module_not_found == "raise":
                raise ValueError(msg)
            elif on_module_not_found == "warn":
                log.warning(msg)
                continue
            else:
                assert_never(on_module_not_found)

        yield module_name


def _merge_modules(*args: Iterable[str]):
    # Merge all modules into a single set
    all_modules = set[str]()

    for modules in args:
        all_modules.update(modules)

    # Sort alphabetically
    return sorted(all_modules)


class SnapshotConfig(C.Config):
    snapshot_dir: Path | None = None
    """The directory to save snapshots to."""

    modules: list[str] = []
    """Modules to snapshot. Default: `[]`."""

    on_module_not_found: Literal["raise", "warn"] = "warn"
    """What to do when a module is not found. Default: `"warn"`."""

    editable_modules: bool = True
    """Snapshot all editable modules. Default: `True`."""

    git_references: dict[str, str] = {}
    """Git references (branch, tag, commit hash) to use for specific modules.
    Key is the module name, value is the git reference. Default: `{}`."""

    def _resolve_modules(self):
        modules = copy.deepcopy(self.modules)
        if self.editable_modules:
            modules = _merge_modules(
                modules, _editable_modules(self.on_module_not_found)
            )

        return modules

    def _resolve_snapshot_dir(self):
        if self.snapshot_dir is None:
            return _default_snapshot_dir()
        return self.snapshot_dir
