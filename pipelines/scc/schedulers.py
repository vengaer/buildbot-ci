""" Buildbot schedulers """

from buildbot.plugins import schedulers, util  # pylint: disable=import-error


def ci_schedulers():
    """Return a list of all schedulers"""
    sched = []
    sched.append(
        schedulers.SingleBranchScheduler(
            name="all",
            change_filter=util.ChangeFilter(branch="master"),
            treeStableTimer=None,
            builderNames=["scc"],
        )
    )
    sched.append(schedulers.ForceScheduler(name="force", builderNames=["scc"]))

    return sched
