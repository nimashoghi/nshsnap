import datetime
from pathlib import Path

import nshconfig as C

from ._config import SnapshotConfig


class SnapshotMetadata(C.Config):
    config: SnapshotConfig
    """The configuration for the snapshot."""

    modules: list[str]
    """The modules that were snapshot."""

    snapshot_dir: Path
    """The directory where the snapshot is saved."""

    timestamp: datetime.datetime
    """The timestamp of the snapshot."""
