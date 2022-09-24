""" Poller generation """

import importlib.util
import inspect
import pathlib
import sys

from buildbot.plugins import changes  # pylint: disable=import-error


def _all_remote_urls():
    """Get all pipeline remote urls"""
    pipeline_dir = (
        pathlib.Path(inspect.getfile(inspect.currentframe())).parent / "pipelines"
    )
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

    return [mod.url for mod in mods]


def git_pollers():
    """Default source pollers"""
    return [
        changes.GitPoller(
            url, workdir="gitpoller-workdir", branch="master", pollInterval=300
        )
        for url in _all_remote_urls()
    ]
