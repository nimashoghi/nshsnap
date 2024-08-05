import logging
from collections.abc import Mapping
from pathlib import Path

import nshconfig as C
from typing_extensions import TypedDict, assert_never, override
from uuid_extensions import uuid7str

from ._util import _gitignored_dir

log = logging.getLogger(__name__)

SNAPSHOT_DIR_NAME_DEFAULT = "nshsnap_snapshots"


class SnapshotConfigKwargsDict(TypedDict, total=False):
    base_dir: Path
    """The base directory to save snapshots to. Default: `~/.cache/nshsnap/"""

    modules: list[str]
    """Additional modules to snapshot. Default: `[]`."""

    editable_modules: bool
    """Whether to include all editable modules. Default: `True`."""

    snapshot_save_dir: Path
    """The directory where the snapshot is saved.
    If not provided, a new directory is created under `base_dir`."""


SNAPSHOT_CONFIG_DEFAULT: SnapshotConfigKwargsDict = {
    "modules": [],
    "editable_modules": True,
}


class SnapshotConfig(C.Config):
    snapshot_dir: Path
    """The directory to save snapshots to."""

    modules: list[str] = []
    """Modules to snapshot. Default: `[]`."""

    @classmethod
    def create(cls, kwargs: SnapshotConfigKwargsDict):
        match kwargs:
            case Mapping():
                kwargs = {**SNAPSHOT_CONFIG_DEFAULT, **kwargs}
            case _:
                assert_never(kwargs)

        assert (base_dir := kwargs.get("base_dir")) is not None, "base_dir is required"
        assert (modules := kwargs.get("modules")) is not None, "modules is required"
        return cls(
            base_dir=base_dir,
            modules=modules,
            editable_modules=kwargs.get("editable_modules", True),
            snapshot_save_dir=kwargs.get("snapshot_save_dir", C.MISSING),
        )
