from agentspring.app_loader import load_app

# Dynamically load the selected app (default: superflow_agent.endpoints)
app_module = load_app()
app = app_module.app 