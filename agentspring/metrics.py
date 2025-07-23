from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from fastapi.responses import Response

def get_or_create_counter(name, documentation, labelnames=()):
    try:
        return REGISTRY._names_to_collectors[name]
    except KeyError:
        return Counter(name, documentation, labelnames=labelnames)

api_requests_total = get_or_create_counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])

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
    @app.middleware('http')
    async def prometheus_metrics_middleware(request, call_next):
        response = await call_next(request)
        api_requests_total.labels(request.method, request.url.path).inc()
        for func in custom_metrics:
            func(request, response)
        return response

    @app.get('/metrics')
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST) 