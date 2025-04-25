from __future__ import annotations

from ._config import SnapshotConfig as SnapshotConfig
from ._load import load_existing_snapshot as load_existing_snapshot
from ._snapshot import ActiveSnapshot as ActiveSnapshot
from ._snapshot import snapshot as snapshot
from ._util import snapshot_id as snapshot_id

SnapshotInfo = ActiveSnapshot

try:
    from . import configs as configs
    from .configs import SnapshotConfigTypedDict as SnapshotConfigTypedDict
except:
    pass


try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # For Python <3.8
    from importlib_metadata import (  # pyright: ignore[reportMissingImports]
        PackageNotFoundError,
        version,
    )

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "unknown"
