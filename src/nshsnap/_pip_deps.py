import importlib.metadata
import importlib.util
import subprocess
from collections.abc import Mapping
from typing import Annotated, Any, Literal, TypeAlias

import nshconfig as C


class BasePackageDependency(C.Config):
    name: str
    version: str | None = None


class RegularPackageDependency(BasePackageDependency):
    type: Literal["regular"] = "regular"


class EditablePackageDependency(BasePackageDependency):
    type: Literal["editable"] = "editable"
    editable_project_location: str

    def importable_module_name(self) -> str | None:
        """
        Attempts to find an importable module name for the package.
        Returns None if no importable module is found.
        """
        try:
            dist = importlib.metadata.distribution(self.name)
            top_level = dist.read_text("top_level.txt")
            if top_level:
                return top_level.strip().split("\n")[0]
        except importlib.metadata.PackageNotFoundError:
            pass

        # Try common naming conventions
        potential_names = [
            self.name,
            self.name.replace("-", "_"),
            self.name.lower(),
            self.name.lower().replace("-", "_"),
        ]

        for name in potential_names:
            if importlib.util.find_spec(name):
                return name

        return None


def _discriminator(value: Any):
    if isinstance(value, Mapping):
        if "editable_project_location" in value:
            return "editable"
        return "regular"
    else:
        if hasattr(value, "editable_project_location"):
            return "editable"
        return "regular"


PackageDependency: TypeAlias = Annotated[
    Annotated[RegularPackageDependency, C.Tag("regular")]
    | Annotated[EditablePackageDependency, C.Tag("editable")],
    C.Discriminator(_discriminator),
]
PipDependencies: TypeAlias = list[PackageDependency]


def current_pip_dependencies():
    return C.TypeAdapter(PipDependencies).validate_json(
        subprocess.run(
            ["pip", "list", "--format=json"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout
    )
