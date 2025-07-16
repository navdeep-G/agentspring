#!/bin/bash

# SupportFlow Agent Startup Script
echo "🚀 Starting SupportFlow Agent with Ollama, Celery, and Redis..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Set environment variables
export CUSTOMER_SUPPORT_AGENT_API_KEY=${CUSTOMER_SUPPORT_AGENT_API_KEY:-demo-key}
export CELERY_BROKER_URL=${CELERY_BROKER_URL:-redis://localhost:6379/0}
export CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND:-redis://localhost:6379/0}

echo "📋 Environment Configuration:"
echo "   API Key: $CUSTOMER_SUPPORT_AGENT_API_KEY"
echo "   Celery Broker: $CELERY_BROKER_URL"
echo "   Celery Backend: $CELERY_RESULT_BACKEND"

# Check for 'rebuild' flag
REBUILD=0
if [[ "$1" == "rebuild" ]]; then
    REBUILD=1
fi

# Stop and (optionally) remove containers and volumes
if [[ $REBUILD -eq 1 ]]; then
    echo "🛑 Stopping and removing existing containers and volumes..."
    docker-compose down -v
    echo "🔨 Rebuilding Docker images without cache..."
    docker-compose build --no-cache
else
    echo "🛑 Stopping existing containers..."
    docker-compose down
fi

# Start the stack
echo "🚀 Starting Docker Compose stack..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Pull required models in Ollama container
echo "📥 Pulling required models in Ollama..."
docker-compose exec -T ollama ollama pull mistral
docker-compose exec -T ollama ollama pull llama3.2

echo "✅ SupportFlow Agent is starting up!"
echo ""
echo "🌐 Access Points:"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000/health"
echo "   Flower Dashboard: http://localhost:5555"
echo "   Ollama: http://localhost:11434"
echo ""
echo "🔑 API Key: $CUSTOMER_SUPPORT_AGENT_API_KEY"
echo ""
echo "📊 Monitor the startup with: docker-compose logs -f"
echo "🛑 Stop the stack with: docker-compose down" 