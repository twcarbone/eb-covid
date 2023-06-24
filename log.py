"""
Logging setup.
"""

import datetime as dt
import logging
import logging.handlers

logger = logging.getLogger("EBCovid")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
fh = logging.FileHandler(filename=f"./logs/EBCovid_{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.log")

fm = logging.Formatter(
    fmt="[%(asctime)s - %(name)s - %(levelname)s] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
)

ch.setFormatter(fm)
fh.setFormatter(fm)

logger.addHandler(ch)
logger.addHandler(fh)
