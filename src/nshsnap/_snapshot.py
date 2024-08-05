import importlib.util
import logging
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import overload

from typing_extensions import Unpack

from ._config import SnapshotConfig, SnapshotConfigKwargsDict

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


@dataclass
class SnapshotInfo:
    snapshot_dir: Path
    """The directory where the snapshot is saved."""

    modules: list[str]
    """The modules that were snapshot."""


def _snapshot_modules(snapshot_dir: Path, modules: list[str]):
    """
    Snapshot the specified modules to the given directory.

    Args:
        snapshot_dir (Path): The directory where the modules will be snapshot.
        modules (Sequence[str]): A sequence of module names to be snapshot.

    Returns:
        Path: The path to the snapshot directory.

    Raises:
        AssertionError: If a module is not found or if a module has a non-directory location.
    """
    log.critical(f"Snapshotting {modules=} to {snapshot_dir}")

    moved_modules = defaultdict[str, list[tuple[Path, Path]]](list)
    for module in modules:
        spec = importlib.util.find_spec(module)
        if spec is None:
            log.warning(f"Module {module} not found")
            continue

        assert (
            spec.submodule_search_locations
            and len(spec.submodule_search_locations) == 1
        ), f"Could not find module {module} in a single location."
        location = Path(spec.submodule_search_locations[0])
        assert (
            location.is_dir()
        ), f"Module {module} has a non-directory location {location}"

        (*parent_modules, module_name) = module.split(".")

        destination = snapshot_dir
        for part in parent_modules:
            destination = destination / part
            destination.mkdir(parents=True, exist_ok=True)
            (destination / "__init__.py").touch(exist_ok=True)

        _copy(location, destination)

        destination = destination / module_name
        log.info(f"Moved {location} to {destination} for {module=}")
        moved_modules[module].append((location, destination))

    return SnapshotInfo(snapshot_dir.absolute(), modules)


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


def _snapshot(config: SnapshotConfig):
    _ensure_supported()

    # Add a .nshsnapconfig file to the directory
    # with the JSON-serialized config
    (config.snapshot_save_dir / ".nshsnapconfig").write_text(
        config.model_dump_json(indent=2)
    )

    return _snapshot_modules(config.snapshot_save_dir, config.modules)


@overload
def snapshot() -> SnapshotInfo: ...


@overload
def snapshot(config: SnapshotConfig, /) -> SnapshotInfo: ...


@overload
def snapshot(**kwargs: Unpack[SnapshotConfigKwargsDict]) -> SnapshotInfo: ...


def snapshot(
    config: SnapshotConfig | None = None,
    /,
    **kwargs: Unpack[SnapshotConfigKwargsDict],
):
    if config is None:
        config = SnapshotConfig.create(kwargs)

    return _snapshot(config)