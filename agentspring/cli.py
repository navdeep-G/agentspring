import os
import sys

TEMPLATE_ENDPOINTS = '''from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def hello():
    """Example endpoint for a new AgentSpring app."""
    return {"message": "Hello from your custom AgentSpring app!"}
'''

TEMPLATE_README = '''# {app_name} (AgentSpring App)

This is a custom app for the AgentSpring framework.

## Usage

export AGENTSPRING_APP={app_dir}.endpoints

'''

def create_app(app_name):
    app_dir = app_name.lower()
    if os.path.exists(app_dir):
        print(f"Directory {app_dir} already exists.")
        sys.exit(1)
    os.makedirs(app_dir)
    with open(os.path.join(app_dir, "endpoints.py"), "w") as f:
        f.write(TEMPLATE_ENDPOINTS)
    with open(os.path.join(app_dir, "README.md"), "w") as f:
        f.write(TEMPLATE_README.format(app_name=app_name, app_dir=app_dir))
    print(f"Created new AgentSpring app in {app_dir}/")

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "create-app":
        print("Usage: python -m agentspring.cli create-app <AppName>")
        sys.exit(1)
    app_name = sys.argv[2]
    create_app(app_name)

if __name__ == "__main__":
    main() 