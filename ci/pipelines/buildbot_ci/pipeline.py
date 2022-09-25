""" buildbot-ci CI pipeline """

from buildbot.plugins import steps, util  # pylint: disable=import-error
from buildbot.plugins import worker  # pylint: disable=import-error
from buildbot_extensions.steps import (  # pylint: disable=import-error, no-name-in-module
    docker,
)

TAG = "buildbot/buildbot-ci"
URL = "https://gitlab.com/vengaer/buildbot-ci.git"


def pipeline(workers: worker.Worker) -> util.BuilderConfig:
    """CI build steps"""
    factory = util.BuildFactory()
    # Check out source
    factory.addStep(
        steps.Git(
            repourl=URL,
            mode="incremental",
            name="Checkout",
        )
    )

    # Build docker image
    factory.addStep(docker.Build(tag=TAG, name="Build Image"))

    # Lint
    factory.addStep(docker.Docker(command=["pylint", "ci"], image=TAG, name="Lint"))

    # Type check
    factory.addStep(docker.Docker(command=["mypy", "ci"], image=TAG, name="Type Check"))

    # Check formatting
    factory.addStep(
        docker.Docker(
            command=["black", "--check", "ci"], image=TAG, name="Check Formatting"
        )
    )

    # Remove dangling docker images
    factory.addStep(docker.Prune(name="Prune"))

    return util.BuilderConfig(
        name="buildbot-ci", workernames=list(workers.keys()), factory=factory
    )
