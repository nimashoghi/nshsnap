import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal, overload

import nshconfig as C
from typing_extensions import Self, TypedDict, Unpack, assert_never

from ._pip_deps import EditablePackageDependency, current_pip_dependencies
from ._resolve_modules import _resolve_parent_modules
from ._util import _gitignored_dir, snapshot_id

log = logging.getLogger(__name__)


class SnapshotResolveModulesConfigKwargsDict(TypedDict, total=False):
    values: Iterable[Any]
    """Values to resolve modules from."""

    deep: Literal["deep", "deep-builtin", "shallow"]
    """How deep to resolve modules. Default: `"deep-builtin"`."""

    ignore_builtin: bool
    """Whether to ignore builtin modules when resolving modules. Default: `True`."""


class SnapshotConfigKwargsDict(TypedDict, total=False):
    snapshot_dir: Path
    """The directory to save snapshots to."""

    modules: list[str]
    """Modules to snapshot. Default: `[]`."""

    editable_modules: bool
    """Snapshot all editable modules. Default: `False`."""

    on_module_not_found: Literal["raise", "warn"]
    """What to do when a module is not found. Default: `"warn"`."""

    resolve_modules: SnapshotResolveModulesConfigKwargsDict
    """Configuration for resolving modules."""


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


def _merge_modules(*args: Iterable[str]):
    # Merge all modules into a single set
    all_modules = set[str]()

    for modules in args:
        all_modules.update(modules)

    # Sort alphabetically
    return sorted(all_modules)


class SnapshotConfig(C.Config):
    snapshot_dir: Path = C.Field(default_factory=_default_snapshot_dir)
    """The directory to save snapshots to."""

    modules: list[str] = []
    """Modules to snapshot. Default: `[]`."""

    on_module_not_found: Literal["raise", "warn"] = "warn"
    """What to do when a module is not found. Default: `"warn"`."""

    @classmethod
    @overload
    def from_kwargs(cls, kwargs: SnapshotConfigKwargsDict, /) -> Self: ...

    @classmethod
    @overload
    def from_kwargs(cls, /, **kwargs: Unpack[SnapshotConfigKwargsDict]) -> Self: ...

    @classmethod
    def from_kwargs(
        cls,
        arg_pos: SnapshotConfigKwargsDict | None = None,
        /,
        **kwargs: Unpack[SnapshotConfigKwargsDict],
    ):
        kwargs = {
            **SNAPSHOT_CONFIG_DEFAULT,
            **(arg_pos or {}),
            **kwargs,
        }
        editable_modules = bool(kwargs.pop("editable_modules"))
        resolve_modules = kwargs.pop("resolve_modules", {})

        instance = cls(**kwargs)  # pyright: ignore[reportCallIssue]

        if editable_modules:
            instance = instance.with_editable_modules()

        if resolve_modules and (values := resolve_modules.get("values")) is not None:
            instance = instance.with_resolved_modules(
                *values,
                deep=resolve_modules.get("deep", "deep-builtin"),
                ignore_builtin=resolve_modules.get("ignore_builtin", True),
            )

        return instance

    def with_editable_modules(
        self,
        on_module_not_found: Literal["raise", "warn"] | None = None,
    ):
        if on_module_not_found is None:
            on_module_not_found = self.on_module_not_found
        return self.model_copy(
            update={
                "modules": _merge_modules(
                    self.modules, _editable_modules(self.on_module_not_found)
                )
            }
        )

    def with_resolved_modules(
        self,
        *args: Any,
        deep: Literal["deep", "deep-builtin", "shallow"] = "deep-builtin",
        ignore_builtin: bool = True,
    ):
        return self.model_copy(
            update={
                "modules": _merge_modules(
                    self.modules,
                    _resolve_parent_modules(
                        args,
                        ignore_builtin=ignore_builtin,
                        deep=deep,
                    ),
                )
            }
        )
