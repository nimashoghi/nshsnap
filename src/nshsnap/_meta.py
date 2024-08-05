import datetime
import re

import nshconfig as C

from ._config import SnapshotConfig


class PackageDependency(C.Config):
    name: str
    version: str | None
    extras: list[str]
    editable: bool
    path: str | None  # For editable installs

    @classmethod
    def from_pip_freeze_line(cls, line: str):
        # Ignore comments and empty lines
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        editable = line.startswith("-e")
        if editable:
            line = line[2:].strip()  # Remove "-e " prefix

        # Parse package name, version, extras, and path
        if editable:
            match = re.match(r"((?:[^=\s]+)(?:\[.+?\])?)(?:\s+@\s+(.+))?", line)
            if not match:
                raise ValueError(f"Invalid editable install line: {line}")
            name_with_extras, path = match.groups()
            version = None
        else:
            match = re.match(r"([^=\s]+)(?:==([^;\s]+))?(?:\s*;\s*(.+))?", line)
            if not match:
                raise ValueError(f"Invalid pip freeze line: {line}")
            name_with_extras, version, path = match.groups()

        # Parse extras
        extras_match = re.match(r"([^[\s]+)(?:\[(.+)\])?", name_with_extras)
        if not extras_match:
            raise ValueError(f"Invalid package name format: {name_with_extras}")
        name, extras_str = extras_match.groups()
        extras = [e.strip() for e in extras_str.split(",")] if extras_str else []

        return cls(
            name=name, version=version, extras=extras, editable=editable, path=path
        )


class PipFreezeParsed(C.Config):
    dependencies: list[PackageDependency]

    @classmethod
    def from_pip_freeze_output(cls, pip_freeze_text: str):
        # Split the pip freeze output into lines and parse each line
        lines = pip_freeze_text.split("\n")
        dependencies = [
            dep
            for dep in (PackageDependency.from_pip_freeze_line(line) for line in lines)
            if dep is not None
        ]
        return cls(dependencies=dependencies)


class SnapshotMetadata(C.Config):
    config: SnapshotConfig
    """The configuration for the snapshot."""

    timestamp: datetime.datetime
    """The timestamp of the snapshot."""

    pip_freeze_parsed: PipFreezeParsed | None
    """The parsed pip freeze output, if available."""

    @classmethod
    def create(cls, config: SnapshotConfig, pip_freeze_text: str | None):
        pip_freeze_parsed = (
            PipFreezeParsed.from_pip_freeze_output(pip_freeze_text)
            if pip_freeze_text
            else None
        )
        return cls(
            config=config,
            timestamp=datetime.datetime.now(),
            pip_freeze_parsed=pip_freeze_parsed,
        )
