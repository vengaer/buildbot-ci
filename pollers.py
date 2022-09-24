""" Poller generation """


from buildbot.plugins import changes  # pylint: disable=import-error
from pipelines import modules


def _all_remote_urls():
    """Get all pipeline remote urls"""
    return [mod.url for mod in modules]


def git_pollers():
    """Default source pollers"""
    return [
        changes.GitPoller(
            url, workdir="gitpoller-workdir", branch="master", pollInterval=300
        )
        for url in _all_remote_urls()
    ]
