""" buildbot-ci CI pipeline """

import sys
from buildbot.plugins import steps, util  # pylint: disable=import-error
from buildbot_extensions.steps import docker
from buildbot.plugins import worker

TAG = "buildbot/buildbot-ci"


def pipeline(workers: worker.Worker) -> util.BuilderConfig:
    """CI build steps"""
    factory = util.BuildFactory()
    # Check out source
    factory.addStep(
        steps.Git(
            repourl="https://gitlab.com/vengaer/buildbot-ci.git",
            mode="incremental",
            name="Checkout",
        )
    )

    # Build docker image
    factory.addStep(docker.Build(tag=TAG, name="Build Image"))

    # Lint
    factory.addStep(
        docker.Docker(command=["pylint", "ci"], image=TAG, name="Lint")
    )

    # Type check
    factory.addStep(
        docker.Docker(command=['mypy', 'ci'], image=TAG, name='Type Check')
    )

    # Check formatting
    factory.addStep(
        docker.Docker(command=['black', '--check', 'ci'], image=TAG, name='Check Formatting')
    )

    # Remove dangling docker images
    factory.addStep(docker.Prune(name="Prune"))

    return util.BuilderConfig(
        name="buildbot-ci", workernames=list(workers.keys()), factory=factory
    )
