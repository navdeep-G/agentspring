# Tool Configuration

## Environment Variables
- `API_KEY`: API key for authentication (required)
- `AGENTSPRING_ENV`: Environment (development, staging, production)
- `LOG_DIR`: Directory for logs (default: logs)
- `SENTRY_DSN`: Sentry DSN for error tracking (optional)
- `CELERY_BROKER_URL`: Celery broker URL (default: redis://localhost:6379/0)

## Security
- RBAC: Use `x-role` header to specify user role (admin, user, guest)
    - Example: `curl -H "x-api-key: demo-key" -H "x-role: admin" http://localhost:8000/some_admin_endpoint`
- Input sanitization: All string inputs are sanitized with `bleach`
- Audit logging: All sensitive actions are logged 

## FAQ & Troubleshooting

- **How do I set secrets in production?**
  Use Kubernetes secrets or environment variables. Never commit secrets to source control.
- **How do I change the API key?**
  Update the `API_KEY` in your environment or secret store and restart the app and workers.
- **How do I debug failed healthchecks?**
  Check logs for errors connecting to Redis, Celery, or missing config.
- **How do I scale the app?**
  Edit the `replicas` field in Docker Compose or Kubernetes manifests.
- **How do I add a new tool or agent?**
  See the orchestration and tool registry sections in the README. 

## How to Add a New Tool
1. Create a new Python function or class in `agentspring/tools/`.
2. Register it with the tool registry:
   ```python
   from agentspring.tools import tool_registry
   
   @tool_registry.register_tool("my_custom_tool")
   def my_custom_tool(arg1: str) -> dict:
       # Your tool logic here
       return {"result": f"Processed {arg1}"}
   ```
3. Add any required dependencies to `requirements.txt`.
4. Document the tool in this file or in your app README.

## How to Test a Tool
1. Write a unit test in `tests/test_tools.py` (create if missing):
   ```python
   def test_my_custom_tool():
       from agentspring.tools import tool_registry
       result = tool_registry.execute_tool("my_custom_tool", arg1="test")
       assert result.result["result"] == "Processed test"
   ```
2. Run `make test` or `pytest agentspring/tests/` to verify.