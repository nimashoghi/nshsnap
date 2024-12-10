from __future__ import annotations

import argparse
import logging
from pathlib import Path

from ._config import SnapshotConfig
from ._snapshot import snapshot


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Create a snapshot of a directory")
    parser.add_argument(
        "-e",
        "--editables",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Snapshot all editable packages in the current environment",
    )
    parser.add_argument(
        "--modules", nargs="*", default=[], help="Additional modules to include"
    )
    parser.add_argument(
        "--dir",
        type=Path,
        required=False,
        help="Custom snapshot directory. If not set, the default is used (~/.cache/nshsnap/snapshots/{tempdir})",
    )
    args = parser.parse_args()

    config = SnapshotConfig.draft()
    config.editable_modules = args.editables
    if args.modules:
        config.modules = args.modules
    elif not config.editable_modules:
        parser.error("At least one of --modules or --editables must be provided")

    if args.dir:
        config.snapshot_dir = args.dir

    config = config.finalize()
    snapshot_info = snapshot(config)

    print(f"Snapshot created at: {snapshot_info.snapshot_dir}")
    print(f"Modules included: {', '.join(snapshot_info.modules)}")
    print("\nTo activate the snapshot, run:")
    print(f"source {snapshot_info.snapshot_dir}/activate")
    print("\nTo execute a command within the snapshot, run:")
    print(f"{snapshot_info.snapshot_dir}/execute <command> [args...]")


if __name__ == "__main__":
    main()
