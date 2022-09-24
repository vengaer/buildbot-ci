""" buildbot_extensions CI pipeline """

from buildbot.plugins import steps, util  # pylint: disable=import-error
from buildbot_extensions.buildbot_extensions.steps import docker

TAG = "buildbot/buildbot-extensions"


def pipeline(workers):
    """CI build steps"""
    factory = util.BuildFactory()
    # Check out source
    factory.addStep(
        steps.Git(
            repourl="https://gitlab.com/vengaer/buildbot_extensions.git",
            mode="incremental",
        )
    )

    # Build docker image
    factory.addStep(docker.Build(tag=TAG))

    # Lint
    factory.addStep(
        docker.Docker(command=["pylint", "buildbot_extensions"], image=TAG, name="Lint")
    )

    # Remove dangling docker images
    factory.addStep(docker.Prune(name="Prune"))

    return util.BuilderConfig(
        name="buildbot-extensions", workernames=list(workers.keys()), factory=factory
    )
