import importlib
import os

from dotenv import load_dotenv

load_dotenv()
from .logging_config import setup_logging

DEFAULT_APP = os.environ.get("AGENTSPRING_APP")


def load_app():
    """Dynamically import and return the selected app's main module."""
    setup_logging()
    module = importlib.import_module(DEFAULT_APP)
    return module
