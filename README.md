# nshsnap

nshsnap is a Python library for creating and managing snapshots of Python projects and environments. It's particularly useful for scenarios where you need to preserve the exact state of your code and dependencies, such as when running machine learning training jobs on cluster systems like SLURM.

## Motivation

When running long-running jobs or experiments, especially in distributed environments, it's critical to maintain consistency in your codebase. Small changes in your project files can lead to crashes or inconsistent results in ongoing runs. nshsnap addresses this issue by allowing you to take a full snapshot of your main development package, preserving the code state at that moment.

This tool was originally created to solve issues encountered when running ML training jobs on SLURM. It enables you to:

1. Capture the current state of your project
2. Ensure reproducibility across multiple runs
3. Isolate changes in your development environment from active jobs

## Installation

You can install nshsnap using pip:

```bash
pip install nshsnap
```

## Usage

### Programmatic Usage

Here's a basic example of how to use nshsnap in your Python code:

```python
from nshsnap import snapshot

# Create a snapshot with default settings
snapshot_info = snapshot()

# Or, create a snapshot with custom configuration
snapshot_info = snapshot(
    modules=["my_project", "my_other_module"],
    editable_modules=True
)

# Create a snapshot with specific git references
snapshot_info = snapshot(
    modules=["my_project", "my_other_module"],
    git_references={
        "my_project": "v1.2.3",        # Use tag v1.2.3
        "my_other_module": "main"      # Use main branch
    },
    editable_modules=False
)

print(f"Snapshot created at: {snapshot_info.snapshot_dir}")
print(f"Modules included: {', '.join(snapshot_info.modules)}")
```

### Command Line Usage

nshsnap also provides a command-line interface:

```bash
# Snapshot all editable packages in the current environment
nshsnap --editables

# Snapshot specific modules
nshsnap --modules my_project my_other_module

# Specify a custom snapshot directory
nshsnap --editables --dir /path/to/snapshot/directory

# Snapshot modules at specific git references
nshsnap --modules my_project --git-ref my_project:v1.2.3
nshsnap --editables --git-ref my_package:main --git-ref another_package:develop

# Get help
nshsnap --help
```

### Snapshot and Run Commands

For convenience, nshsnap provides the `nshsnap-run` command that creates a snapshot and immediately runs a command within that environment:

```bash
# Run a Python module within a snapshot
nshsnap-run --modules my_project python -m my_project.main

# Run a script with all editable packages
nshsnap-run --editables python my_script.py

# Run with specific git references
nshsnap-run --modules my_project --git-ref my_project:v1.2.3 python -m my_project.main

# Run with custom snapshot directory
nshsnap-run --modules my_project --dir /tmp/my_snapshot python train.py

# Get help
nshsnap-run --help
```

### Activating and Using Snapshots

After creating a snapshot, all you need to do is prepend the snapshot directory to your `PYTHONPATH` to activate the snapshot environment:

```bash
export PYTHONPATH=/path/to/snapshot:$PYTHONPATH
```

You can also activate or execute commands within the snapshot environment using our helper scripts:

```bash
# Activate the snapshot environment
source /path/to/snapshot/.bin/activate

# Execute a command within the snapshot environment
/path/to/snapshot/.bin/execute python my_script.py
```

## Features

- Snapshot editable packages and specified modules
- **Git reference support**: Snapshot modules at specific git branches, tags, or commit hashes
- **Snapshot and run**: Create snapshots and immediately execute commands within them using `nshsnap-run`
- Preserve exact state of code and dependencies
- Easy activation and execution within snapshot environments
- Integration with version control systems (respects .gitignore)
- Metadata storage for snapshot information

### Git References

nshsnap supports snapshotting modules at specific git references (branches, tags, or commit hashes). This is particularly useful when you want to ensure your snapshot uses a specific version of a dependency:

- **Modules must be git repositories**: The git reference feature only works for modules that are located in git repositories
- **Automatic restoration**: After snapshotting, the original git reference is automatically restored
- **Error handling**: If a git reference cannot be checked out, nshsnap will log an error and skip that module
- **Multiple references**: You can specify different git references for different modules

```bash
# Example: Snapshot with git references
nshsnap --modules my_project other_module \
        --git-ref my_project:v2.1.0 \
        --git-ref other_module:feature-branch
```

## Requirements

- Python 3.9+
- git
- rsync

## Contributing

Contributions to nshsnap are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
