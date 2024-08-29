# Setup logger for module
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False

# formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# console handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# file handler
# fh = logging.FileHandler("lpu.log")
# fh.setFormatter(formatter)
# logger.addHandler(fh)
