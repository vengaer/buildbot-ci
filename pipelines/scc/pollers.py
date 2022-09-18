""" scc CI repository pollers """

from buildbot.plugins import changes  # pylint: disable=import-error

from .config import __url__


def ci_poller():
    """Default source poller"""
    return changes.GitPoller(
        __url__, workdir="gitpoller-workdir", branch="master", pollInterval=300
    )
