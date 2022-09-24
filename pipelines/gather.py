import importlib.util
import inspect
import pathlib
import sys


def _ci_modules():
    """Load all pipeline modules"""
    pipeline_dir = pathlib.Path(inspect.getfile(inspect.currentframe())).parent
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
    mods = list(map(importlib.util.module_from_spec, specs))

    for spec, mod in zip(specs, mods):
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)

    return mods


modules = _ci_modules()


def gather(workers):
    return [m.pipeline(workers) for m in modules]
