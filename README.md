# nshsnap

nshsnap is a Python library for creating and managing snapshots of Python projects and environments. It's particularly useful for scenarios where you need to preserve the exact state of your code and dependencies, such as when running machine learning training jobs on cluster systems like SLURM.

## Table of Contents <!-- omit in toc -->
- [nshsnap](#nshsnap)
    - [Motivation](#motivation)
    - [Installation](#installation)
    - [Usage](#usage)
        - [Programmatic Usage](#programmatic-usage)
        - [Command Line Usage](#command-line-usage)
        - [Activating and Using Snapshots](#activating-and-using-snapshots)
    - [Features](#features)
    - [Requirements](#requirements)
    - [Contributing](#contributing)
    - [License](#license)


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

# Get help
nshsnap --help
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
- Preserve exact state of code and dependencies
- Easy activation and execution within snapshot environments
- Integration with version control systems (respects .gitignore)
- Metadata storage for snapshot information

## Requirements

- Python 3.10+
- git
- rsync

## Contributing

Contributions to nshsnap are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
