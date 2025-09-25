FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly install pypdf and other required packages
RUN pip install --no-cache-dir \
    pydantic-settings>=2.0.0 \
    alembic \
    sqlalchemy[asyncio] \
    asyncpg \
    pypdf>=3.17.0 \
    fastapi-limiter \
    prometheus-client

# Install application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["bash", "-c", "\
    echo 'Waiting for database...' && \
    until PGPASSWORD=postgres psql -h postgres -U postgres -d postgres -c 'SELECT 1' >/dev/null 2>&1; do \
        echo 'Waiting for PostgreSQL...'; \
        sleep 1; \
    done && \
    echo 'Running migrations...' && \
    alembic upgrade head && \
    echo 'Starting server...' && \
    pip list && \
    uvicorn agentspring.main:app --host 0.0.0.0 --port 8000 --reload"]
