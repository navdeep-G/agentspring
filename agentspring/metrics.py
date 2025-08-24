from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Histogram,
    generate_latest,
)

# API Metrics
REQUEST_COUNTER = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "http_status"],
)

# Tool Metrics
TOOL_USAGE_COUNTER = Counter(
    "tool_executions_total",
    "Total number of tool executions",
    ["tool_name", "status"],  # status can be 'success' or 'failure'
)

TOOL_LATENCY_HISTOGRAM = Histogram(
    "tool_execution_latency_seconds",
    "Latency of tool executions",
    ["tool_name"],
)

# LLM Metrics
LLM_REQUEST_COUNTER = Counter(
    "llm_requests_total",
    "Total number of LLM requests",
    ["model_name", "status"],
)

LLM_TOKEN_COUNTER = Counter(
    "llm_tokens_total",
    "Total number of LLM tokens processed",
    ["model_name", "token_type"],  # token_type can be 'prompt' or 'completion'
)

LLM_LATENCY_HISTOGRAM = Histogram(
    "llm_request_latency_seconds", "Latency of LLM requests", ["model_name"]
)


def get_metrics():
    """Generate latest metrics."""
    return generate_latest(REGISTRY)


from fastapi.responses import Response


def get_or_create_counter(name, documentation, labelnames=()):
    try:
        return REGISTRY._names_to_collectors[name]
    except KeyError:
        return Counter(name, documentation, labelnames=labelnames)


api_requests_total = get_or_create_counter(
    "api_requests_total", "Total API requests", ["method", "endpoint"]
)

# List of user-registered custom metric functions
custom_metrics = []


def register_custom_metric(metric_func):
    """
    Register a custom metric function.
    The function should accept (request, response) and update any Prometheus metric.
    Example:
        my_counter = get_or_create_counter('my_counter', 'My custom counter')
        def my_metric(request, response):
            my_counter.inc()
        register_custom_metric(my_metric)
    """
    custom_metrics.append(metric_func)


def setup_metrics(app):
    @app.middleware("http")
    async def prometheus_metrics_middleware(request, call_next):
        response = await call_next(request)
        api_requests_total.labels(request.method, request.url.path).inc()
        for func in custom_metrics:
            func(request, response)
        return response

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
