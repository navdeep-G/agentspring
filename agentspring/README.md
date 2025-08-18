# AgentSpring Framework

> **Note:** This README is for framework contributors and advanced users. For general usage, setup, and high-level documentation, see the [main README](../README.md).


This directory contains the core framework code for AgentSpring.

## Core Modules

-   **`api.py`**: FastAPI integration and the `FastAPIAgent` base class. It now includes lazy initialization for the `AsyncTaskManager`, allowing the agent to run without a Redis dependency.
-   **`orchestration.py`**: The agentic orchestration engine for LLM-driven tool chaining.
-   **`tools/`**: The modular tool registry.
-   **`llm.py`**: LLM integration helpers and prompt templates.
-   **`models.py`**: Core Pydantic models for the framework.
-   **`tasks.py`**: Asynchronous task management with Celery.
-   **`metrics.py`**: Prometheus metrics for monitoring and observability.

## How to Extend the Framework

-   **Add New Tools**: Create new tools in the `agentspring/tools/` directory and register them with the `@tool_registry.register()` decorator.
-   **Customize Orchestration**: Modify the prompt templates in `llm.py` or extend the `orchestration.py` module to create new orchestration strategies.
-   **Extend Models**: Add new Pydantic models to `models.py` for data validation and serialization.

For more detailed examples, setup instructions, and advanced usage, please see the [main README.md](../README.md).