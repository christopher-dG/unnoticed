import logging
import sys

from .monitor import monitorloop  # noqa
from .util import DBROOT, notify  # noqa

logging.basicConfig(
    filename="unnoticed.log",
    level=logging.WARNING,
)
logging.getLogger("watchdog").setLevel(logging.INFO)
logging.getLogger().setLevel(
    logging.DEBUG if "debug" in sys.argv else logging.INFO
)
