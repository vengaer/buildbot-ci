from buildbot.plugins import steps, util  # pylint: disable=import-error
from buildbot.plugins import worker  # pylint: disable=import-error
from buildbot_extensions.steps import (  # pylint: disable=import-error,no-name-in-module
    docker,
)
from buildbot_extensions.steps.docker import (  # pylint: disable=import-error,no-name-in-module
    cargo,
)

TAG = "buildbot/asman"
URL = "https://gitlab.com/vengaer/asman.git"


def pipeline(workers: worker.Worker) -> util.BuilderConfig:
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

    # Build
    factory.addStep(cargo.Build(image=TAG, name="Build"))

    # Tests
    factory.addStep(cargo.Test(image=TAG, name="Test"))

    # Lint
    factory.addStep(cargo.Check(image=TAG, name="Lint"))

    # Docs
    factory.addStep(cargo.Doc(image=TAG, name="Doc"))

    # Remove dangling docker images
    factory.addStep(docker.Prune(name="Prune"))

    return util.BuilderConfig(
        name="asman", workernames=list(workers.keys()), factory=factory
    )
