import functools
import logging
import sys
from collections import abc
from typing import Any, Literal

from typing_extensions import assert_never

log = logging.getLogger(__name__)

_builtin_or_std_modules = sys.stdlib_module_names.union(sys.builtin_module_names)


@functools.cache
def _resolve_leaf_module(module: str, ignore_builtin: bool):
    # First, resolve the module name into its first part. E.g.,:
    # mymodule.submodule.MyClass => mymodule
    module = module.split(".", 1)[0]

    # Ignore builtin or standard library modules
    if ignore_builtin and module in _builtin_or_std_modules:
        return ()

    return (module,)


def _resolve_type(
    type_: type,
    cached: dict[str, set[str]],
    ignore_builtin: bool = True,
    deep: Literal["deep", "deep-builtin", "shallow"] = "deep-builtin",
):
    if (cached_modules := cached.get(type_.__module__)) is not None:
        return cached_modules

    modules = set[str]()

    # Resolve the module of the type
    modules.update(_resolve_leaf_module(type_.__module__, ignore_builtin))

    # Resolve the module of the type's bases
    if deep == "deep":
        for base in type_.__bases__:
            modules.update(_resolve_type(base, cached, ignore_builtin, deep))

    cached[type_.__module__] = modules
    return modules


def _filter_container_deep(
    value: abc.Collection | abc.Mapping,
    deep: Literal["deep", "deep-builtin", "shallow"],
):
    match deep:
        case "deep":
            return True
        # When deep="deep-builtin", we only look inside containers if they are built-in types.
        # In other words, whenever we hit a user-defined class, we stop looking inside it.
        case "deep-builtin":
            return (
                _resolve_leaf_module(type(value).__module__, ignore_builtin=True) == ()
            )
        case "shallow":
            return False
        case _:
            assert_never(deep)


def _resolve_modules_from_value(
    value: Any,
    cached: dict[str, set[str]],
    ignore_builtin: bool = True,
    deep: Literal["deep", "deep-builtin", "shallow"] = "deep-builtin",
):
    """
    Resolve the modules from the given value.

    The core idea here that we want to take a list of given arguments to our runner, and resolve them into a list of modules that we want to snapshot.

    The `deep` parameter controls how deep we search for modules inside the given value. The possible values are:
    - "deep": Search for modules inside the given value and all of its sub-values. This unpacks any types that implement the `abc.Collection` or `abc.Mapping` abstract base classes. This also looks at MRO of types.
    - "deep-builtin": Same as "deep", but only search inside built-in types. This is useful when we want to avoid looking inside user-defined classes.
    - "shallow": Only search for modules in the given value itself.

    Example below:
    ```python
    # module: mymodule.submodule

    class MyClass: pass

    _resolve_modules_from_value("mymodule.submodule.MyClass") => []
    _resolve_modules_from_value(MyClass) => ["mymodule.submodule"]
    _resolve_modules_from_value(MyClass()) => ["mymodule.submodule"]
    _resolve_modules_from_value((MyClass(),)) => ["mymodule.submodule"]
    _resolve_modules_from_value(({"key": [MyClass()]},)) => ["mymodule.submodule"]

    ```
    """
    modules: set[str] = set()
    is_type = False

    match value:
        # If type, resolve the module from the type
        # + all of its bases
        case type():
            modules.update(_resolve_type(value, cached, ignore_builtin, deep))
            is_type = True
        # If a primitive python type, just process the value
        case (
            int()
            | float()
            | str()
            | bool()
            | complex()
            | bytes()
            | bytearray()
            | None
        ):
            pass
        # If a collection, resolve the module from each item.
        # First, we handle mappings because we need to resolve
        # the modules from the keys and values separately.
        case abc.Mapping() if _filter_container_deep(value, deep):
            for key, value in value.items():
                modules.update(
                    _resolve_modules_from_value(
                        key,
                        cached,
                        ignore_builtin=ignore_builtin,
                    )
                )
                modules.update(
                    _resolve_modules_from_value(
                        value,
                        cached,
                        ignore_builtin=ignore_builtin,
                    )
                )
        # Now, we handle any other collection
        case abc.Collection() if _filter_container_deep(value, deep):
            for item in value:
                modules.update(
                    _resolve_modules_from_value(
                        item,
                        cached,
                        ignore_builtin=ignore_builtin,
                    )
                )
        # Anything else that has a "__module__" attribute
        case _ if hasattr(value, "__module__"):
            modules.update(_resolve_leaf_module(value.__module__, ignore_builtin))
        case _:
            pass

    # We should also resolve the type of the value, if it's not a type itself
    if not is_type:
        modules.update(
            _resolve_modules_from_value(
                type(value),
                cached,
                ignore_builtin=ignore_builtin,
            )
        )

    return modules


def _resolve_parent_modules(
    values: abc.Sequence[Any],
    ignore_builtin: bool = True,
    deep: Literal["deep", "deep-builtin", "shallow"] = "deep-builtin",
):
    modules = set[str]()
    cached = dict[str, set[str]]()  # we can keep a global set of visited modules

    for value in values:
        value_modules = _resolve_modules_from_value(
            value,
            cached,
            ignore_builtin=ignore_builtin,
            deep=deep,
        )
        if "__main__" in value_modules:
            log.warning(
                f"Config class (or a child class) {value.__class__.__name__} is defined in the main script.\n"
                "Snapshotting the main script is not supported.\n"
                "Skipping snapshotting of the config class's module."
            )
            value_modules.remove("__main__")

        modules.update(value_modules)

    return list(modules)
