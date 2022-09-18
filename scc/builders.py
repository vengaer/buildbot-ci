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
    factory.addStep(docker.Docker(command=["make", "-j", nproc()], image=TAG))

    # Tests
    factory.addStep(docker.Docker(command=["make", "-j", nproc(), "check"], image=TAG))

    # Configure and run fuzzer
    command = ['conftool', 'generate defconfig']
    for var, val in (
        ("CONFIG_FUZZ_TIME", 10),
        ("CONFIG_FUZZ_LENGTH", 32768),
        ("CONFIG_FUZZ_TIMEOUT", 10),
    ):
        command += ['&&', 'conftool', 'set', var, val]

    for fuzz_target in FUZZ_TARGETS:
        cmd = command + ['&&', 'conftool', 'set', 'CONFIG_FUZZ_TARGET', fuzz_target]
        cmd += ['&&', 'make', '-j', nproc(), 'fuzz']

        factory.addStep(
            docker.Docker(command=cmd, image=TAG)
        )

    # Lint
    factory.addStep(docker.Docker(command=["make", "-j", nproc(), "lint"], image=TAG))

    # Docs
    factory.addStep(docker.Docker(command=["make", "-j", nproc(), "docs"], image=TAG))

    # Remove dangling docker images
    factory.addStep(docker.Prune())

    return util.BuilderConfig(
        name="scc", workernames=list(workers.keys()), factory=factory
    )
