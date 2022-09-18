""" scc CI builders """

import multiprocessing

from buildbot.plugins import steps, util  # pylint: disable=import-error
from buildbot_extensions.buildbot_extensions.steps import docker

FUZZ_TARGETS = ["hashmap", "hashtab", "rbtree", "svec", "btree", "lower_bound"]

TAG = "buildbot/scc"


def nproc():
    """Get number of processors on build host"""
    return str(multiprocessing.cpu_count())


def ci_builder(workers):
    """CI build steps"""
    factory = util.BuildFactory()
    # Check out source
    factory.addStep(
        steps.Git(repourl="https://gitlab.com/vengaer/scc.git", mode="incremental")
    )

    # Build docker image
    factory.addStep(docker.Build(tag=TAG))

    # Build
    factory.addStep(
        docker.Docker(command=["make", "-j", nproc()], image=TAG, name="Build")
    )

    # Tests
    factory.addStep(
        docker.Docker(command=["make", "-j", nproc(), "check"], image=TAG, name="Check")
    )

    # Configure fuzzer
    factory.addStep(docker.Volume(volume="scc_persistent", name="Persistent Volume"))
    factory.addStep(
        docker.Docker(
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
            docker.Docker(
                command=["conftool", "-c", "/scc_persistent/config", "set", var, val],
                volumes=["scc_persistent"],
                image=TAG,
                name=f"Set {var}",
            )
        )

    # Fuzz targets
    for fuzz_target in FUZZ_TARGETS:
        factory.addStep(
            docker.Docker(
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
                name="Set CONFIG_FUZZ_TARGET",
            )
        )
        factory.addStep(
            docker.Docker(
                command=[
                    "make",
                    "-j",
                    nproc(),
                    "fuzz",
                    "CONFIG=/scc_persistent/config",
                ],
                volumes=["scc_persistent"],
                image=TAG,
                name=f"Fuzz {fuzz_target}",
            )
        )

    # Lint
    factory.addStep(
        docker.Docker(command=["make", "-j", nproc(), "lint"], image=TAG, name="Lint")
    )

    # Docs
    factory.addStep(
        docker.Docker(command=["make", "-j", nproc(), "docs"], image=TAG, name="Docs")
    )

    # Remove dangling docker images
    factory.addStep(docker.Prune(), name="Prune")

    return util.BuilderConfig(
        name="scc", workernames=list(workers.keys()), factory=factory
    )
