"""Dynamically load a module/package from an arbitrary location"""

import importlib.util
import os
import sys
import types
import typing

import trappedbot


class DynloadSpecError(BaseException):
    pass


class DynloadDuplicateModuleError(BaseException):
    pass


def dynamically_load_module(name: str, path: str) -> types.ModuleType:
    """Load a module or package from a dynamic location

    This allows users to write custom Python code for bot tasks

    name:   A name for the module.
            Take care that this is GLOBALLY UNIQUE for this Python process.
    path:   The path to the module.

    It will return the module to the caller.
    To use it, the caller must save the result and call it that way;
    it will not be usable via standard Python 'import'.
    (If you want that, install the module as a Python package to the Python path
    before starting Python.)
    """

    if name in sys.modules:
        raise DynloadDuplicateModuleError(name)

    # If the user passes a directory, assume it is a Python package
    module_path = path if not os.path.isdir(path) else os.path.join(path, "__init__.py")

    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None:
        raise DynloadSpecError(name, path)

    dynmod = importlib.util.module_from_spec(spec)
    sys.modules[name] = dynmod
    spec.loader.exec_module(dynmod)

    return dynmod


def trappedbot_dynload_for_taskfunc(
    name: str, path: str
) -> typing.Optional[types.FunctionType]:
    """Dynamically load a module and return a trappedbot taskfunc

    The taskfunc must be named 'trappedbot_task' exactly,
    and it must have the TaskFunc signature.
    """
    dynmod_name = f"trappedbot_extension_{name}"

    try:
        dynmod = dynamically_load_module(dynmod_name, path)
    except DynloadSpecError:
        trappedbot.LOGGER.error(
            f"Could not dynamically load a module called {dynmod_name} from {path} because it could not find a Python module or package at that location."
        )
        return None
    except DynloadDuplicateModuleError:
        trappedbot.LOGGER.error(
            f"Could not dynamically load a module called {dynmod_name} from {path} because a module with that name already exists."
        )
        return None

    try:
        taskfunc = dynmod.trappedbot_task
    except AttributeError:
        trappedbot.LOGGER.error(
            f"Cannot use dynamically loaded module called {dynmod_name} from {path} because it does not export a 'trappedbot_task' function"
        )
        return None

    return taskfunc