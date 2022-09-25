""" buildbot_extensions CI pipeline """

import sys
from buildbot.plugins import steps, util  # pylint: disable=import-error
from buildbot_extensions.steps import docker
from buildbot.plugins import worker

TAG = "buildbot/buildbot-extensions"


def pipeline(workers: worker.Worker) -> util.BuilderConfig:
    """CI build steps"""
    factory = util.BuildFactory()
    # Check out source
    factory.addStep(
        steps.Git(
            repourl="https://gitlab.com/vengaer/buildbot_extensions.git",
            mode="incremental",
            name="Checkout",
        )
    )

    # Build docker image
    factory.addStep(docker.Build(tag=TAG, name="Build Image"))

    # Lint
    factory.addStep(
        docker.Docker(command=["pylint", "buildbot_extensions"], image=TAG, name="Lint")
    )

    # Remove dangling docker images
    factory.addStep(docker.Prune(name="Prune"))

    return util.BuilderConfig(
        name="buildbot-extensions", workernames=list(workers.keys()), factory=factory
    )
