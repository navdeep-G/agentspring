# AgentSpring

AgentSpring is a flexible, production-ready framework for building, running, and scaling intelligent agent applications. It is designed to help you create agents that can process tasks, make decisions, interact with users, and orchestrate complex workflows—all with robust observability, security, and extensibility.

While AgentSpring provides a strong foundation and many enterprise features out of the box, it is also designed to be extended and adapted to your specific needs. We encourage users to build on top of the framework, add new tools, and customize agent behaviors for their own use cases.

## Key Features

- **Dynamic agent loading:** Easily switch between different agent apps by changing a config variable.
- **Async and batch task processing:** Agents can process long-running or background jobs, and you can track their status/results.
- **Multi-tenancy:** Run agents for multiple customers or teams, each in their own isolated context.
- **Audit logging and observability:** All agent actions are logged and observable in real time via Prometheus and Grafana.
- **Security and RBAC:** API key authentication and role-based access control for agent endpoints.
- **Extensible tool registry and orchestration:** Add new tools, workflows, or agent types with minimal code changes.
- **Docker Compose and Kubernetes support:** Production-like local testing and scalable cloud deployment.
- **Custom metrics:** Register and expose your own Prometheus metrics for agent actions.

## What AgentSpring Is (and Isn't)

AgentSpring aims to provide a solid, extensible base for agentic applications, but it is not a "magic bullet" or a one-size-fits-all solution. You may need to:
- Extend or adapt the framework for your domain-specific needs
- Add new tools, agent types, or integrations
- Write additional tests to reach your desired coverage
- Tune deployment and observability for your environment

We strive to make AgentSpring as useful and adaptable as possible, but we recognize that every production system is unique.

## Example: Customer Support Agent

AgentSpring includes a customer support agent example that can:
- Classify incoming messages
- Detect urgency
- Summarize issues
- Route tickets to the right team
- Process requests asynchronously or in batch
- Expose custom and default metrics for observability

## Getting Started

1. **Clone the repo and install dependencies**
2. **Configure your `.env` file** (see `env.example`)
3. **Run locally with Docker Compose:**
   ```bash
   docker-compose -f docker-compose.full.yml up --build
   ```
4. **Access the API:** [http://localhost:8000/docs](http://localhost:8000/docs)
5. **View metrics:** [http://localhost:8000/metrics](http://localhost:8000/metrics)
6. **Prometheus:** [http://localhost:9090](http://localhost:9090)
7. **Grafana:** [http://localhost:3000](http://localhost:3000) (admin/admin)

## Kubernetes Deployment

See the `k8s/` directory and README sections for instructions on deploying to Kubernetes. The provided manifests are a starting point and may need to be adapted for your environment.

## Customization and Extensibility

- **Add new agent apps:** Create a new module with an `app` variable and set `AGENTSPRING_APP` in your `.env`.
- **Register custom tools:** Add to the `agentspring/tools/` directory and orchestrate them in your agent logic.
- **Add custom metrics:** Use `register_custom_metric` from `agentspring.metrics`.
- **Extend orchestration:** Use or extend the `AgentOrchestrator` for more complex workflows.

## Limitations and Next Steps

AgentSpring is a strong foundation, but you may want to:
- Add more advanced agentic features (planning, memory, multi-agent collaboration)
- Integrate with external APIs or business systems
- Expand test coverage and add more example agents
- Tune for your specific production environment

We welcome feedback and contributions to make AgentSpring even more useful for the community.

---

*Thank you for considering AgentSpring. We hope it helps you build the agentic systems you need, and we look forward to seeing what you create!*