import inspect
import importlib
import os

from buildbot.plugins import schedulers, util  # pylint: disable=import-error


def generate(builders):
    """Return a list of all schedulers"""
    sched = []
    names = [b.name for b in builders]
    sched.append(
        schedulers.SingleBranchScheduler(
            name="all",
            change_filter=util.ChangeFilter(branch="master"),
            treeStableTimer=None,
            builderNames=names,
        )
    )
    sched.append(schedulers.ForceScheduler(name="Force", builderNames=names))

    return sched
