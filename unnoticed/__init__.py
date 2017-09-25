import logging

from .monitor import monitorloop  # noqa
from .util import DBROOT, notify  # noqa

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    filename="unnoticed.log",
    level=logging.WARNING,
)
logging.getLogger("watchdog").setLevel(logging.INFO)
logging.getLogger().setLevel(logging.INFO)
