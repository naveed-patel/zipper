import logging

__app_name__ = "Zipper"
__version__ = "0.1.0"

# Static configuration
CONFIG = {
    "preferred_parser": "typer",  # Valid choice typer, argparse
}

LOG_FORMAT = "%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:%(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

logger = logging.getLogger(__name__)
