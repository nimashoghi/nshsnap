import logging
from collections.abc import Mapping
from pathlib import Path

import nshconfig as C
from typing_extensions import TypedDict, assert_never
from uuid_extensions import uuid7str

from ._util import _gitignored_dir

log = logging.getLogger(__name__)


class SnapshotConfigKwargsDict(TypedDict, total=False):
    snapshot_dir: Path
    """The directory to save snapshots to."""

    modules: list[str]
    """Modules to snapshot. Default: `[]`."""


SNAPSHOT_CONFIG_DEFAULT: SnapshotConfigKwargsDict = {}


def _default_snapshot_dir() -> Path:
    snaps_folder = Path.home() / ".cache" / "nshsnap" / "snapshots"
    snaps_folder.mkdir(parents=True, exist_ok=True)

    return _gitignored_dir(snaps_folder / uuid7str(), create=True)


class SnapshotConfig(C.Config):
    snapshot_dir: Path = C.Field(default_factory=_default_snapshot_dir)
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

        return cls(**kwargs)
