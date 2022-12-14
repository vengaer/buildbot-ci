import json
from typing import Any, Dict

from buildbot.plugins import worker  # pylint: disable=import-error

from . import pipelines
from . import pollers
from . import schedulers

# This is a sample buildmaster config file. It must be installed as
# 'master.cfg' in your buildmaster's base directory.

# This is the dictionary that the buildmaster pays attention to. We also use
# a shorter alias to save typing.
BuildmasterConfig: Dict[str, Any] = {}
c = BuildmasterConfig

####### WORKERS

OPTFILE = "/var/lib/buildbot/options.json"

with open(OPTFILE, "r", encoding="ascii") as handle:
    options = json.load(handle)

workers = options["workers"]

# The 'workers' list defines the set of recognized workers. Each element is
# a Worker object, specifying a unique worker name and password.  The same
# worker name and password must be configured on the worker.
c["workers"] = [worker.Worker(w, p) for w, p in workers.items()]

# 'protocols' contains information about protocols which master will use for
# communicating with workers. You must define at least 'port' option that workers
# could connect to your master with this protocol.
# 'port' must match the value configured into the workers (with their
# --master option)
c["protocols"] = {"pb": {"port": 9989}}

####### CHANGESOURCES

# the 'change_source' setting tells the buildmaster how it should find out
# about source code changes.

c["change_source"] = []
c["change_source"] += pollers.git_pollers()

####### BUILDERS

c["builders"] = []
c["builders"] += pipelines.gather(workers)

####### SCHEDULERS

# Configure the Schedulers, which decide how to react to incoming changes.  In this
# case, just kick off a 'runtests' build

c["schedulers"] = schedulers.generate(c["builders"])

####### BUILDBOT SERVICES

# 'services' is a list of BuildbotService items like reporter targets. The
# status of each build will be pushed to these targets. buildbot/reporters/*.py
# has a variety to choose from, like IRC bots.

c["services"] = []

####### PROJECT IDENTITY

# the 'title' string will appear at the top of this buildbot installation's
# home pages (linked to the 'titleURL').

c["title"] = "Buildbot CI"
c["titleURL"] = "https://gitlab.com/vengaer/buildbot-ci"

# the 'buildbotURL' string should point to the location where the buildbot's
# internal web server is visible. This typically uses the port number set in
# the 'www' entry below, but with an externally-visible host name which the
# buildbot cannot figure out without some help.

c["buildbotURL"] = "http://192.168.0.127:8010/"

# minimalistic config to activate new web UI
c["www"] = dict(
    port=8010, plugins=dict(waterfall_view={}, console_view={}, grid_view={})
)

####### DB URL

c["db"] = {
    # This specifies what database buildbot uses to store its state.
    # It's easy to start with sqlite, but it's recommended to switch to a dedicated
    # database, such as PostgreSQL or MySQL, for use in production environments.
    # http://docs.buildbot.net/current/manual/configuration/global.html#database-specification
    "db_url": "sqlite:///state.sqlite",
}
