import importlib.util
import inspect
import pathlib
import sys

from typing import List
from types import ModuleType

from buildbot.plugins import util, worker  # pylint: disable=import-error


def _ci_modules() -> List[ModuleType]:
    """Load all pipeline modules"""
    frame = inspect.currentframe()
    if frame is None:
        raise RuntimeError("Could not get current frame")
    pipeline_dir = pathlib.Path(inspect.getfile(frame)).parent
    modpaths = [
        p for p in pipeline_dir.glob("*") if p.is_dir() and (p / "__init__.py").exists()
    ]

    specs = list(
        map(
            lambda p: importlib.util.spec_from_file_location(
                p.name, str(p / "__init__.py")
            ),
            modpaths,
        )
    )
    if any((s is None for s in specs)):
        raise RuntimeError("Could not load module specs")

    mods = list(map(importlib.util.module_from_spec, specs))  # type: ignore

    for spec, mod in zip(specs, mods):
        sys.modules[spec.name] = mod  # type: ignore
        spec.loader.exec_module(mod)  # type: ignore

    return mods


modules = _ci_modules()


def gather(workers: worker.Worker) -> List[util.BuilderConfig]:
    return [m.pipeline(workers) for m in modules]
