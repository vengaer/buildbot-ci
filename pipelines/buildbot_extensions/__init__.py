""" Continuous integration for buildbot_extensions
    https://gitlab.com/vengaer/buildbot_extensions
 """

from .builders import ci_builder
from .config import __url__
from .pollers import ci_poller
