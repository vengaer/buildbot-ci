""" scc CI builders """

from buildbot.plugins import steps, util  # pylint: disable=import-error
from buildbot_extensions.buildbot_extensions.steps import docker


def ci_builder(workers):
    """CI build steps"""
    factory = util.BuildFactory()
    factory.addStep(
        steps.Git(repourl="https://gitlab.com/vengaer/scc.git", mode="incremental")
    )
    factory.addStep(steps.ShellCommand(command=["make", "docker-image"]))
    factory.addStep(docker.Build(dockerfile="Dockerfile", tag="buildbot/scc"))
    factory.addStep(
        docker.Docker(command=["make"], container="buildbot/scc", workdir="/scc")
    )
    factory.addStep(docker.Prune())

    return util.BuilderConfig(
        name="scc", workernames=list(workers.keys()), factory=factory
    )
