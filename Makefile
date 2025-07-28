.PHONY: help redis ollama celery api test test_examples all clean install venv lint format stop restart

# Default environment variables
export CUSTOMER_SUPPORT_AGENT_API_KEY=demo-key
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/0

help:
	@echo "Available targets:"
	@echo "  redis     Start Redis server (requires redis-server in PATH)"
	@echo "  ollama    Start Ollama server (requires ollama in PATH)"
	
	
	@echo "  test      Run pytest for customer_support_agent example"
	@echo "  all       Start all services (except Redis/Ollama) and run tests"
	@echo "  clean     Remove build, dist, __pycache__, *.pyc, egg-info"
	@echo "  install   Install Python requirements in .venv"
	@echo "  venv      Create Python virtual environment (.venv)"
	@echo "  lint      Run flake8 linter (if installed)"
	@echo "  format    Run black code formatter (if installed)"
	@echo "  stop      Kill background dev servers (uvicorn, celery)"
	@echo "  restart   Stop then start all (except Redis/Ollama) and run tests"

# Start Redis server (background)
redis:
	redis-server &

# Start Ollama server (background)
ollama:
	ollama serve &

# Start Celery worker for customer_support_agent

	.venv/bin/celery -A  worker --loglevel=info

# Start FastAPI app for customer_support_agent

	.venv/bin/uvicorn examples.customer_support_agent.endpoints:agent.app --reload

# Run unit tests for agentspring
# (You will need to add tests in agentspring/tests/)
test:
	@echo "[Test] Ensuring Redis is running..."
	@if ! lsof -i :6379 | grep LISTEN > /dev/null; then \
		echo "[Test] Starting Redis server in background..."; \
		redis-server & \
		sleep 2; \
	else \
		echo "[Test] Redis is already running."; \
	fi
	@echo "[Test] Running pytest..."
	pytest agentspring/tests/ --maxfail=3 --disable-warnings -v

# Run pytest for customer_support_agent example

	pytest 
# Start Celery worker and FastAPI app in background, then run tests
all:
	@echo "Starting Celery worker and FastAPI app in background, then running tests..."
	( .venv/bin/celery -A  worker --loglevel=info & )
	sleep 5
	( .venv/bin/uvicorn  --reload & )
	sleep 5
	.venv/bin/pytest 

# Remove build artifacts and caches
clean:
	rm -rf dist build .pytest_cache .venv __pycache__ agentspring.egg-info */__pycache__ */*/__pycache__ *.pyc */*.pyc */*/*.pyc

# Install Python requirements in .venv
install:
	.venv/bin/pip install --upgrade pip && .venv/bin/pip install -r requirements.txt

# Create Python virtual environment
venv:
	python3 -m venv .venv

# Run flake8 linter (if installed)
lint:
	@.venv/bin/flake8 . || echo "flake8 not installed. Run 'make install' and 'pip install flake8' in .venv."

# Run black code formatter (if installed)
format:
	@.venv/bin/black . || echo "black not installed. Run 'make install' and 'pip install black' in .venv."

# Kill background dev servers (uvicorn, celery)
stop:
	pkill -f "uvicorn" || true
	pkill -f "celery" || true

# Stop then start all (except Redis/Ollama) and run tests
restart:
	$(MAKE) stop
	sleep 2
	$(MAKE) all 