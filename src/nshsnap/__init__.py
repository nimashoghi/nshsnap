from __future__ import annotations

from ._config import SnapshotConfig as SnapshotConfig
from ._load import load_existing_snapshot as load_existing_snapshot
from ._snapshot import SnapshotInfo as SnapshotInfo
from ._snapshot import snapshot as snapshot
from ._util import snapshot_id as snapshot_id

try:
    from . import configs as configs
    from .configs import SnapshotConfigTypedDict as SnapshotConfigTypedDict
except:
    pass
