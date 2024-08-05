from pathlib import Path


def _gitignored_dir(path: Path, *, create: bool = True) -> Path:
    if create:
        path.mkdir(exist_ok=True, parents=True)
    assert path.is_dir(), f"{path} is not a directory"

    gitignore_path = path / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.touch()
        gitignore_path.write_text("*\n")

    return path


def _create_activation_script(script_dir: Path):
    activate_script = script_dir / "activate"
    script_content = f"""
#!/bin/bash

# Add the snapshot directory to PYTHONPATH
export PYTHONPATH="{script_dir}:$PYTHONPATH"

# Optionally, you can modify the PS1 to indicate that the snapshot is active
export OLD_PS1="$PS1"
export PS1="(snapshot) $PS1"

deactivate() {{
    # Restore the old PYTHONPATH
    export PYTHONPATH="${{PYTHONPATH#{script_dir}:}}"

    # Restore the old PS1
    export PS1="$OLD_PS1"
    unset OLD_PS1

    # Remove the deactivate function
    unset -f deactivate
}}

echo "Snapshot environment activated. Use 'deactivate' to exit."
"""
    activate_script.write_text(script_content)
    activate_script.chmod(0o755)  # Make the script executable


def _create_execution_script(script_dir: Path):
    execute_script = script_dir / "execute"
    script_content = f"""
#!/bin/bash

if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <command> [args...]"
    exit 1
fi

# Add the snapshot directory to PYTHONPATH
export PYTHONPATH="{script_dir}:$PYTHONPATH"

# Execute the given command
exec "$@"
"""
    execute_script.write_text(script_content)
    execute_script.chmod(0o755)  # Make the script executable


def create_snapshot_scripts(script_dir: Path):
    # Create the activation script
    _create_activation_script(script_dir)

    # Create the execution script
    _create_execution_script(script_dir)
