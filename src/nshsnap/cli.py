from __future__ import annotations

import argparse
import logging
from pathlib import Path

from ._config import SnapshotConfig
from ._snapshot import snapshot
from ._util import print_snapshot_usage


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
    parser.add_argument(
        "--git-ref",
        action="append",
        metavar="MODULE:REF",
        help="Specify git reference for a module (format: module_name:git_reference). "
        "Can be used multiple times. Only works for modules that are git repositories.",
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

    # Parse git references
    if args.git_ref:
        git_references = {}
        for git_ref_spec in args.git_ref:
            if ":" not in git_ref_spec:
                parser.error(
                    f"Invalid git reference format '{git_ref_spec}'. "
                    "Expected format: module_name:git_reference"
                )
            module_name, git_ref = git_ref_spec.split(":", 1)
            git_references[module_name] = git_ref
        config.git_references = git_references

    config = config.finalize()
    snapshot_info = snapshot(config)

    print(f"Snapshot created at: {snapshot_info.snapshot_dir}")
    print(f"Modules included: {', '.join(snapshot_info.modules)}")

    # Show git reference information
    git_ref_modules = [
        module_info
        for module_info in snapshot_info.module_infos
        if module_info.git_reference_used
    ]
    if git_ref_modules:
        print("\nGit references used:")
        for module_info in git_ref_modules:
            print(f"  {module_info.name}: {module_info.git_reference_used}")

    # Show any failures
    failed_modules = [
        module_info
        for module_info in snapshot_info.module_infos
        if module_info.status in ("not_found", "git_reference_failed")
    ]
    if failed_modules:
        print("\nWarnings/Errors:")
        for module_info in failed_modules:
            if module_info.status == "not_found":
                print(f"  {module_info.name}: Module not found")
            elif module_info.status == "git_reference_failed":
                ref = module_info.git_reference_requested
                print(f"  {module_info.name}: Failed to use git reference '{ref}'")

    print_snapshot_usage(snapshot_info.snapshot_dir)


if __name__ == "__main__":
    main()
