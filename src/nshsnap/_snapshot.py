from __future__ import annotations

import importlib.util
import logging
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Literal

from typing_extensions import assert_never

from ._config import SnapshotConfig
from ._meta import SnapshotMetadata
from ._util import (
    checkout_git_reference,
    create_snapshot_scripts,
    gitignored_dir,
    is_git_repository,
    restore_git_reference,
)

if TYPE_CHECKING:
    from . import configs

log = logging.getLogger(__name__)


def _copy(source: Path, location: Path):
    """
    Copy files from the source directory to the specified location, excluding ignored files.

    Args:
        source (Path): The path to the source directory.
        location (Path): The path to the destination directory.

    Raises:
        CalledProcessError: If the rsync command fails.

    """
    ignored_files = (
        subprocess.check_output(
            [
                "git",
                "-C",
                str(source),
                "ls-files",
                "--exclude-standard",
                "-oi",
                "--directory",
            ]
        )
        .decode("utf-8")
        .splitlines()
    )

    # run rsync with .git folder and `ignored_files` excluded
    _ = subprocess.run(
        [
            "rsync",
            "-a",
            "--exclude",
            ".git",
            *(f"--exclude={file}" for file in ignored_files),
            str(source),
            str(location),
        ],
        check=True,
    )


@dataclass(frozen=True, slots=True)
class SnapshotModuleInfo:
    __nshconfig_config__: ClassVar = {"disable_typed_dict_generation": True}

    name: str
    """The name of the module."""

    status: Literal["success", "not_found", "git_reference_failed"]
    """The status of the module."""

    location: Path | None
    """The location of the module, if found."""

    destination: Path | None
    """The destination where the module was copied to, if applicable."""

    git_reference_requested: str | None = None
    """The git reference that was requested for this module."""

    git_reference_original: str | None = None
    """The original git reference before snapshotting."""

    git_reference_used: str | None = None
    """The git reference that was actually used for snapshotting."""


@dataclass(frozen=True, slots=True)
class ActiveSnapshot:
    __nshconfig_config__: ClassVar = {"disable_typed_dict_generation": True}

    config: SnapshotConfig
    """The configuration used to create the snapshot."""

    snapshot_dir: Path
    """The directory where the snapshot is saved."""

    module_infos: list[SnapshotModuleInfo]
    """Information about the modules included in the snapshot."""

    @property
    def modules(self) -> list[str]:
        """The list of modules included in the snapshot."""
        return [
            module.name for module in self.module_infos if module.status == "success"
        ]


def _normalize_module_locations(
    module: str,
    raw_locations: Iterable[str],
) -> list[Path]:
    """
    Turn the raw ``spec.submodule_search_locations`` into a clean list of
    directories:

    1. ``Path(entry).resolve()`` to normalise and remove “./” aliases.
    2. Keep only entries that are real directories (filters editable-install
       hooks such as “__editable__.pkg-0.0.0.finder.__path_hook__”).
    3. Remove duplicates while preserving order.

    Returns
    -------
    list[Path]
        Cleaned list of locations.  May be empty if nothing usable is left.
    """
    seen: set[Path] = set()
    locations: list[Path] = []

    for entry in raw_locations:
        p = Path(entry).expanduser().resolve()
        if not p.is_dir():
            continue  # skip non-directory hooks
        if p in seen:
            continue  # drop duplicates
        seen.add(p)
        locations.append(p)

    if not locations:
        log.debug(
            "Module %s had no usable directory locations after normalisation: %s",
            module,
            raw_locations,
        )
    return locations


def _snapshot_modules(
    snapshot_dir: Path,
    modules: list[str],
    on_module_not_found: Literal["raise", "warn"],
    git_references: dict[str, str] | None = None,
):
    """
    Snapshot the specified modules to the given directory.

    Args:
        snapshot_dir (Path): The directory where the modules will be snapshot.
        modules (Sequence[str]): A sequence of module names to be snapshot.
        on_module_not_found: What to do when a module is not found.
        git_references: Optional mapping of module names to git references.

    Returns:
        Path: The path to the snapshot directory.

    Raises:
        AssertionError: If a module is not found or if a module has a non-directory location.
        ValueError: If a git reference is specified for a non-git repository.
    """
    if git_references is None:
        git_references = {}

    log.critical(f"Snapshotting {modules=} to {snapshot_dir}")

    module_infos: list[SnapshotModuleInfo] = []
    git_restore_info: list[tuple[Path, str]] = []  # (path, original_reference)

    try:
        for module in modules:
            git_ref_requested = git_references.get(module)

            if (spec := importlib.util.find_spec(module)) is None:
                msg = f"Module {module} not found"
                if on_module_not_found == "raise":
                    raise ValueError(msg)
                elif on_module_not_found == "warn":
                    log.warning(msg)
                    module_infos.append(
                        SnapshotModuleInfo(
                            name=module,
                            status="not_found",
                            location=None,
                            destination=None,
                            git_reference_requested=git_ref_requested,
                        )
                    )
                    continue
                else:
                    assert_never(on_module_not_found)

            raw_search_locations = spec.submodule_search_locations or []
            locations = _normalize_module_locations(module, raw_search_locations)
            if not locations:
                raise ValueError(
                    f"Module {module!r} has no importable directory locations "
                    f"({raw_search_locations})"
                )

            if len(locations) > 1:
                log.warning(
                    "Module %s is a namespace package with multiple locations: %s. "
                    "Using the first location %s.",
                    module,
                    locations,
                    locations[0],
                )
            location = locations[0]

            git_ref_original = None
            git_ref_used = None

            # Handle git reference if specified
            if git_ref_requested:
                if not is_git_repository(location):
                    msg = (
                        f"Module {module} at {location} is not a git repository, "
                        f"but git reference '{git_ref_requested}' was specified. "
                        "Only git repositories support git references."
                    )
                    log.error(msg)
                    module_infos.append(
                        SnapshotModuleInfo(
                            name=module,
                            status="git_reference_failed",
                            location=location,
                            destination=None,
                            git_reference_requested=git_ref_requested,
                        )
                    )
                    continue

                try:
                    # Get current reference and checkout the requested one
                    git_ref_original = checkout_git_reference(
                        location, git_ref_requested
                    )
                    git_restore_info.append((location, git_ref_original))
                    git_ref_used = git_ref_requested
                    log.info(
                        f"Switched {module} from '{git_ref_original}' to '{git_ref_requested}'"
                    )
                except subprocess.CalledProcessError as e:
                    msg = f"Failed to checkout git reference '{git_ref_requested}' for module {module}: {e}"
                    log.error(msg)
                    module_infos.append(
                        SnapshotModuleInfo(
                            name=module,
                            status="git_reference_failed",
                            location=location,
                            destination=None,
                            git_reference_requested=git_ref_requested,
                            git_reference_original=git_ref_original,
                        )
                    )
                    continue

            (*parent_modules, module_name) = module.split(".")

            destination = snapshot_dir
            for part in parent_modules:
                destination = destination / part
                destination.mkdir(parents=True, exist_ok=True)
                (destination / "__init__.py").touch(exist_ok=True)

            _copy(location, destination)

            destination = destination / module_name
            log.info(f"Moved {location} to {destination} for {module=}")
            module_infos.append(
                SnapshotModuleInfo(
                    name=module,
                    status="success",
                    location=location,
                    destination=destination,
                    git_reference_requested=git_ref_requested,
                    git_reference_original=git_ref_original,
                    git_reference_used=git_ref_used,
                )
            )
    finally:
        # Restore all git repositories to their original references
        for location, original_ref in git_restore_info:
            restore_git_reference(location, original_ref)

    return snapshot_dir.absolute(), module_infos


def _ensure_supported():
    # Make sure we have git and rsync installed
    try:
        subprocess.run(
            ["git", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "git is not installed. Please install git to use snapshot."
        )

    try:
        subprocess.run(
            ["rsync", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "rsync is not installed. Please install rsync to use snapshot."
        )


def _snapshot_meta(config: SnapshotConfig, snapshot_dir: Path):
    meta_dir = snapshot_dir / ".nshsnapmeta"
    meta_dir.mkdir(exist_ok=True)

    # Save the config
    (meta_dir / "config.json").write_text(config.model_dump_json(indent=4))

    # Dump the current pip environment and save it
    try:
        pip_freeze = subprocess.run(
            ["pip", "freeze", "--local"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout
        (meta_dir / "requirements.txt").write_text(pip_freeze)
    except BaseException as e:
        log.warning(f"Failed to dump pip environment: {e}")
        pip_freeze = None

    # Save the metadata
    meta = SnapshotMetadata.create(config)
    (meta_dir / "meta.json").write_text(meta.model_dump_json(indent=4))

    # Create the activation and execution scripts
    script_dir = snapshot_dir / ".bin"
    script_dir.mkdir(exist_ok=True)
    create_snapshot_scripts(snapshot_dir, script_dir)


def _snapshot(config: SnapshotConfig):
    _ensure_supported()

    snapshot_dir = config._resolve_snapshot_dir()
    modules = config._resolve_modules()

    gitignored_dir(snapshot_dir)
    _snapshot_meta(config, snapshot_dir)

    snapshot_dir, modules = _snapshot_modules(
        snapshot_dir, modules, config.on_module_not_found, config.git_references
    )
    return ActiveSnapshot(config, snapshot_dir, modules)


def snapshot(config: configs.SnapshotConfigInstanceOrDict | None = None, /):
    from . import configs

    if config is None:
        config = SnapshotConfig()

    config = configs.CreateSnapshotConfig(config)
    return _snapshot(config)
