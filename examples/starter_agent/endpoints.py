from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def hello():
    """Example endpoint for the Starter Agent app."""
    return {"message": "Hello from your Starter Agent app!"}

# To use this app, set AGENTFLOW_APP=template_agent.endpoints and run main.py 