import logging
import sys

from .monitor import monitorloop  # noqa
from .util import dbroot, notify  # noqa


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.WARNING)
if "debug" in sys.argv:
    logging.getLogger().setLevel(logging.DEBUG)
