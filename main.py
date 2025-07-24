import os
import importlib

def load_app():
    app_path = os.environ.get("AGENTSPRING_APP", "examples.customer_support_agent.endpoints")
    module = importlib.import_module(app_path)
    return getattr(module, "app")

app = load_app() 