# Tool Configuration

## Environment Variables
- `API_KEY`: API key for authentication (required)
- `AGENTSPRING_ENV`: Environment (development, staging, production)
- `LOG_DIR`: Directory for logs (default: logs)
- `SENTRY_DSN`: Sentry DSN for error tracking (optional)
- `CELERY_BROKER_URL`: Celery broker URL (default: redis://localhost:6379/0)

## Security
- RBAC: Use `x-role` header to specify user role (admin, user, guest)
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