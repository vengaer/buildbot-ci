""" scc CI builders """

import multiprocessing

from buildbot.plugins import steps, util  # pylint: disable=import-error
from buildbot.plugins import worker  # pylint: disable=import-error
from buildbot_extensions.steps import (  # pylint: disable=import-error,no-name-in-module
    docker,
)

FUZZ_TARGETS = ["hashmap", "hashtab", "rbtree", "svec", "btree", "lower_bound"]

TAG = "buildbot/scc"
URL = "https://gitlab.com/vengaer/scc.git"


def nproc() -> str:
    """Get number of processors on build host"""
    return str(multiprocessing.cpu_count())


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

    # Build
    factory.addStep(
        docker.ShellCommand(command=["make", "-j", nproc()], image=TAG, name="Build")
    )

    # Configure
    factory.addStep(
        docker.Volume(
            volume="scc_persistent", permissions="777", name="Persistent Volume"
        )
    )

    factory.addStep(
        docker.ShellCommand(
            command=[
                "conftool",
                "-c",
                "/scc_persistent/config",
                "generate",
                "defconfig",
            ],
            volumes=["scc_persistent"],
            image=TAG,
            name="Generate Defconfig",
        )
    )

    for var, val in (
        ("CONFIG_FUZZ_TIME", 10),
        ("CONFIG_FUZZ_LENGTH", 32768),
        ("CONFIG_FUZZ_TIMEOUT", 10),
    ):
        factory.addStep(
            docker.ShellCommand(
                command=["conftool", "-c", "/scc_persistent/config", "set", var, val],
                volumes=["scc_persistent"],
                image=TAG,
                name=f"Set {var}",
            )
        )

    for chunksize in (1, 2, 32, 64, 256):
        factory.addStep(
            docker.ShellCommand(
                command=[
                    "conftool",
                    "-c",
                    "/scc_persistent/config",
                    "set",
                    "CONFIG_ARENA_CHUNKSIZE",
                    str(chunksize),
                ],
                image=TAG,
                name=f"Set CONFIG_ARENA_CHUNKSIZE={chunksize}",
            )
        )

        # Tests
        factory.addStep(
            docker.ShellCommand(
                command=["make", "-j", nproc(), "check"],
                image=TAG,
                name=f"Check w/ chunksize={chunksize}",
            )
        )

        # Fuzz targets
        for fuzz_target in FUZZ_TARGETS:
            factory.addStep(
                docker.ShellCommand(
                    command=[
                        "conftool",
                        "-c",
                        "/scc_persistent/config",
                        "set",
                        "CONFIG_FUZZ_TARGET",
                        fuzz_target,
                    ],
                    volumes=["scc_persistent"],
                    image=TAG,
                    name=f"Set target {fuzz_target} w/ chunksize {chunksize}",
                )
            )
            factory.addStep(
                docker.ShellCommand(
                    command=[
                        "make",
                        "-j",
                        nproc(),
                        "fuzz",
                        "CONFIG=/scc_persistent/config",
                    ],
                    volumes=["scc_persistent"],
                    image=TAG,
                    name=f"Fuzz {fuzz_target} w/ chunksize={chunksize}",
                )
            )

    # Lint
    factory.addStep(
        docker.ShellCommand(
            command=["make", "-j", nproc(), "lint"], image=TAG, name="Lint"
        )
    )

    # Docs
    factory.addStep(
        docker.ShellCommand(
            command=["make", "-j", nproc(), "docs"], image=TAG, name="Docs"
        )
    )

    # Remove dangling docker images
    factory.addStep(docker.Prune(name="Prune"))

    return util.BuilderConfig(
        name="scc", workernames=list(workers.keys()), factory=factory
    )
