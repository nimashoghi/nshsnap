from __future__ import annotations

import importlib.util
import logging
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from typing_extensions import assert_never

from ._config import SnapshotConfig
from ._meta import SnapshotMetadata
from ._util import _gitignored_dir, create_snapshot_scripts

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


@dataclass
class SnapshotInfo:
    snapshot_dir: Path
    """The directory where the snapshot is saved."""

    modules: list[str]
    """The modules that were snapshot."""

    @property
    def metadata_dir(self) -> Path:
        return self.snapshot_dir / ".nshsnapmeta"


def _snapshot_modules(
    snapshot_dir: Path,
    modules: list[str],
    on_module_not_found: Literal["raise", "warn"],
):
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
        if (spec := importlib.util.find_spec(module)) is None:
            msg = f"Module {module} not found"
            match on_module_not_found:
                case "raise":
                    raise ValueError(msg)
                case "warn":
                    log.warning(msg)
                    continue
                case _:
                    assert_never(on_module_not_found)

        assert (
            spec.submodule_search_locations
            and len(spec.submodule_search_locations) == 1
        ), f"Could not find module {module} in a single location."
        location = Path(spec.submodule_search_locations[0])
        assert location.is_dir(), (
            f"Module {module} has a non-directory location {location}"
        )

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

    _gitignored_dir(snapshot_dir)
    _snapshot_meta(config, snapshot_dir)
    return _snapshot_modules(snapshot_dir, modules, config.on_module_not_found)


def snapshot(config: configs.SnapshotConfigInstanceOrDict | None = None, /):
    from . import configs

    if config is None:
        config = SnapshotConfig()

    config = configs.CreateSnapshotConfig(config)
    return _snapshot(config)
