from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from uuid_extensions import uuid7str

log = logging.getLogger(__name__)


def gitignored_dir(path: Path, *, create: bool = True) -> Path:
    if create:
        path.mkdir(exist_ok=True, parents=True)
    assert path.is_dir(), f"{path} is not a directory"

    gitignore_path = path / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.touch()
        gitignore_path.write_text("*\n")

    return path


def _create_activation_script(snapshot_dir: Path, script_dir: Path):
    """Create activation scripts for bash, zsh, fish and PowerShell."""
    # Template strings
    bash_tpl = f"""#!/usr/bin/env bash
# Add the snapshot directory to PYTHONPATH
export PYTHONPATH="{snapshot_dir}:$PYTHONPATH"

export OLD_PS1="$PS1"
export PS1="(snapshot) $PS1"

deactivate() {{
    export PYTHONPATH="${{PYTHONPATH#{snapshot_dir}:}}"
    export PS1="$OLD_PS1"
    unset OLD_PS1
    unset -f deactivate
}}
echo "Snapshot environment activated. Use 'deactivate' to exit."
"""

    # zsh is syntactically compatible with the bash template above
    zsh_tpl = bash_tpl.replace("/usr/bin/env bash", "/usr/bin/env zsh")

    fish_tpl = f"""#!/usr/bin/env fish
# Add the snapshot directory to PYTHONPATH
set -gx PYTHONPATH "{snapshot_dir}:$PYTHONPATH"

function deactivate
    set -gx PYTHONPATH (string replace -r '^{snapshot_dir}:' '' $PYTHONPATH)
    functions -e deactivate
end
echo "Snapshot environment activated. Use 'deactivate' to exit."
"""

    ps1_tpl = f"""# PowerShell activation script
$env:PYTHONPATH = "{snapshot_dir};" + $env:PYTHONPATH
function global:deactivate {{
    $env:PYTHONPATH = $env:PYTHONPATH -replace [regex]::Escape("{snapshot_dir};"), ''
    Remove-Item Function:\\deactivate
}}
Write-Host "Snapshot environment activated. Use 'deactivate' to exit."
"""

    # Script mapping
    scripts: dict[str, str] = {
        "activate": bash_tpl,
        "activate.zsh": zsh_tpl,
        "activate.fish": fish_tpl,
        "activate.ps1": ps1_tpl,
    }

    # Write scripts
    for name, content in scripts.items():
        fp = script_dir / name
        fp.write_text(content)
        # Make the script executable where it makes sense
        if not name.endswith(".ps1"):
            fp.chmod(0o755)


def _create_execution_script(snapshot_dir: Path, script_dir: Path):
    execute_script = script_dir / "execute"
    script_content = f"""#!/bin/bash

if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <command> [args...]"
    exit 1
fi

# Add the snapshot directory to PYTHONPATH
export PYTHONPATH="{snapshot_dir}:$PYTHONPATH"

# Execute the given command
exec "$@"
"""
    execute_script.write_text(script_content)
    execute_script.chmod(0o755)  # Make the script executable


def create_snapshot_scripts(snapshot_dir: Path, script_dir: Path):
    # Create the activation script
    _create_activation_script(snapshot_dir, script_dir)

    # Create the execution script
    _create_execution_script(snapshot_dir, script_dir)


def snapshot_id():
    return uuid7str()


def is_git_repository(path: Path) -> bool:
    """Check if the given path is a git repository."""
    try:
        subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--git-dir"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_current_git_reference(path: Path) -> str:
    """Get the current git reference (branch or commit hash) of the repository."""
    try:
        # Try to get the current branch name
        result = subprocess.run(
            ["git", "-C", str(path), "symbolic-ref", "--short", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # If not on a branch, get the commit hash
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.stdout.strip()


def checkout_git_reference(path: Path, reference: str) -> str:
    """
    Checkout the specified git reference and return the previous reference.

    Args:
        path: The path to the git repository
        reference: The git reference to checkout (branch, tag, or commit hash)

    Returns:
        The previous git reference that was checked out

    Raises:
        subprocess.CalledProcessError: If the git operation fails
        ValueError: If the path is not a git repository
    """
    if not is_git_repository(path):
        raise ValueError(f"Path {path} is not a git repository")

    # Get the current reference before switching
    current_ref = get_current_git_reference(path)

    try:
        # Checkout the specified reference
        subprocess.run(
            ["git", "-C", str(path), "checkout", reference],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        log.info(f"Checked out git reference '{reference}' in {path}")
        return current_ref
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else ""
        raise subprocess.CalledProcessError(
            e.returncode,
            e.cmd,
            f"Failed to checkout git reference '{reference}' in {path}: {stderr}",
        )


def restore_git_reference(path: Path, reference: str) -> None:
    """
    Restore the git repository to the specified reference.

    Args:
        path: The path to the git repository
        reference: The git reference to restore to

    Raises:
        subprocess.CalledProcessError: If the git operation fails
    """
    try:
        subprocess.run(
            ["git", "-C", str(path), "checkout", reference],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        log.info(f"Restored git reference '{reference}' in {path}")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else ""
        log.error(f"Failed to restore git reference '{reference}' in {path}: {stderr}")
        # Don't raise here as this is a cleanup operation


def print_snapshot_usage(snapshot_dir: Path) -> None:
    """
    Display how to activate the snapshot and run commands inside it for the
    supported shells.
    """
    bin_dir = snapshot_dir / ".bin"
    print("\nTo activate the snapshot, run:")
    print(f"  bash/zsh   : source {bin_dir}/activate")
    print(f"  fish       : source {bin_dir}/activate.fish")
    print(f"  PowerShell : {bin_dir}\\activate.ps1")
    print("\nTo execute a command within the snapshot, run:")
    print(f"  {bin_dir}/execute <command> [args...]")
