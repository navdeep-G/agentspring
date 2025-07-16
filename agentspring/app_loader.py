import importlib
import os

DEFAULT_APP = os.environ.get("AGENTSPRING_APP", "examples.customer_support_agent.endpoints")

def load_app():
    """Dynamically import and return the selected app's main module."""
    module = importlib.import_module(DEFAULT_APP)
    return module
