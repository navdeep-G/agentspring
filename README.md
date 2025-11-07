# AgentSpring: A Framework for Building AI Agents

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?logo=docker)](https://www.docker.com/)

## 🌟 What is AgentSpring?

AgentSpring is an open-source framework designed to simplify the development, deployment, and management of AI agents. It provides a robust set of tools and abstractions that enable developers to create sophisticated AI-powered applications with minimal boilerplate code.

## 🚀 Key Features

- **🤖 Intelligent Agents**: Create stateful, context-aware AI agents with custom behaviors
- **🔧 Tool System**: Extend agent capabilities with custom tools and functions
- **🧩 Plugin Architecture**: Modular design for easy extension and customization
- **⚡ FastAPI Backend**: Built on FastAPI for high-performance API endpoints
- **📦 Container Ready**: Docker and Docker Compose support for easy deployment
- **🔒 Secure**: Built-in authentication and authorization
- **📊 Monitoring**: Integrated logging and monitoring capabilities

## 🏗️ Project Structure

```
agentspring/
├── agents/              # Core agent implementations
├── api/                 # FastAPI application and endpoints
├── db/                  # Database models and migrations
├── tools/               # Built-in tools for agents
├── demos/               # Example implementations
│   └── travel_planner/  # Example travel planning agent
├── tests/               # Test suite
├── Dockerfile           # Docker configuration
└── requirements.txt     # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (for production)
- Redis (for caching and message brokering)
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agentspring.git
   cd agentspring
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running with Docker (Recommended)

1. Start all services:
   ```bash
   docker-compose up -d
   ```

2. Check the logs:
   ```bash
   docker-compose logs -f
   ```

3. Access the API at `http://localhost:8000`

## 🧑‍💻 Basic Usage

### Creating a Simple Agent

```python
from agentspring import Agent, Message, MessageRole

class GreetingAgent(Agent):
    """A simple agent that greets users."""
    
    async def execute(self, messages, context=None):
        last_message = messages[-1]
        name = last_message.get('name', 'there')
        return Message(
            role=MessageRole.ASSISTANT, 
            content=f"Hello, {name}! How can I assist you today?"
        )

# Initialize and use the agent
agent = GreetingAgent()
response = await agent.execute([{"role": "user", "content": "Hi!", "name": "Alex"}])
print(response.content)
```

### Running the Travel Planner Demo

1. Navigate to the demo directory:
   ```bash
   cd demos/travel_planner
   ```

2. Run the demo:
   ```bash
   python travel_planner.py
   ```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
