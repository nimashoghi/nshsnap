from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys

from ._snapshot import snapshot
from .cli import add_parser_arguments, parsed_args_to_config


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Create a snapshot and run a command within it",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a Python module within a snapshot of mymodule
  nshsnap-run --modules mymodule -- python -m mymodule.main

  # Run a script with snapshot of all editable packages
  nshsnap-run --editables -- python my_script.py

  # Run with specific git references
  nshsnap-run --modules mymodule --git-ref mymodule:v1.2.3 -- python -m mymodule.main

  # Run with custom snapshot directory
  nshsnap-run --modules mymodule --dir /tmp/my_snapshot -- python -m mymodule.main

Note: Use -- to separate snapshot options from the command to run.
        """,
    )
    parser = add_parser_arguments(parser)
    parser.add_argument(
        "command",
        nargs="*",
        help="Command to execute after snapshot options. "
        "Prefix the command with -- if it starts with a dash.",
    )
    args = parser.parse_args()
    logging.info("Parsed arguments: %s", args)
    command_args = args.command

    # Validate that a command was provided
    if not command_args:
        parser.error(
            "No command provided. Please specify a command to run after snapshot options "
            "(prefix the command with -- if it starts with a dash)."
        )

    # Validate snapshot configuration and convert parsed arguments to config
    config = parsed_args_to_config(args, parser)

    # Create the snapshot
    logging.info("Creating snapshot...")
    snapshot_info = snapshot(config)

    logging.info("Snapshot created at: %s", snapshot_info.snapshot_dir)
    logging.info("Modules included: %s", ", ".join(snapshot_info.modules))

    # Show git reference information
    git_ref_modules = [
        module_info
        for module_info in snapshot_info.module_infos
        if module_info.git_reference_used
    ]
    if git_ref_modules:
        logging.info("Git references used:")
        for module_info in git_ref_modules:
            logging.info("  %s: %s", module_info.name, module_info.git_reference_used)

    # Show any failures
    failed_modules = [
        module_info
        for module_info in snapshot_info.module_infos
        if module_info.status in ("not_found", "git_reference_failed")
    ]
    if failed_modules:
        logging.warning("Warnings/Errors:")
        for module_info in failed_modules:
            if module_info.status == "not_found":
                logging.warning("  %s: Module not found", module_info.name)
            elif module_info.status == "git_reference_failed":
                ref = module_info.git_reference_requested
                logging.warning(
                    "  %s: Failed to use git reference '%s'", module_info.name, ref
                )

    logging.info("Executing command: %s", " ".join(command_args))

    # Set up the environment with the snapshot directory in PYTHONPATH
    env = os.environ.copy()
    if current_pythonpath := env.get("PYTHONPATH"):
        env["PYTHONPATH"] = f"{snapshot_info.snapshot_dir}:{current_pythonpath}"
    else:
        env["PYTHONPATH"] = str(snapshot_info.snapshot_dir)

    # Execute the command within the snapshot environment
    try:
        result = subprocess.run(command_args, env=env)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        logging.info("Command interrupted")
        sys.exit(130)  # Standard exit code for SIGINT
    except FileNotFoundError as e:
        logging.error("Command not found: %s", e)
        sys.exit(127)  # Standard exit code for command not found
    except Exception as e:
        logging.exception("Error executing command: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
