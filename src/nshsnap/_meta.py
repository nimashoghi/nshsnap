import datetime

import nshconfig as C

from ._config import SnapshotConfig
from ._pip_deps import PipDependencies, current_pip_dependencies


class SnapshotMetadata(C.Config):
    config: SnapshotConfig
    """The configuration for the snapshot."""

    timestamp: datetime.datetime
    """The timestamp of the snapshot."""

    pip_dependencies: PipDependencies | None
    """The parsed dependencies from the output of `pip list --format=json`."""

    @classmethod
    def create(
        cls,
        config: SnapshotConfig,
        pip_dependencies: PipDependencies | None = None,
    ):
        if pip_dependencies is None:
            pip_dependencies = current_pip_dependencies()
        return cls(
            config=config,
            timestamp=datetime.datetime.now(),
            pip_dependencies=pip_dependencies,
        )
