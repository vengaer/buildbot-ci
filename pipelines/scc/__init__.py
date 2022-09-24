""" Continuous integration for scc
    https://gitlab.com/vengaer/scc.git
"""

from .builders import ci_builder
from .config import __url__
from .pollers import ci_poller
