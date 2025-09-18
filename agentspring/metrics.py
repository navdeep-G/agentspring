from fastapi import Response, FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
REQUEST_COUNTER = Counter("api_requests_total","Total number of API requests",["method","endpoint","http_status"])
REQUEST_LATENCY = Histogram("api_request_latency_seconds","Request latency (seconds)",["endpoint"])
def setup_metrics(app: FastAPI):
    @app.middleware("http")
    async def prometheus_metrics_middleware(request, call_next):
        with REQUEST_LATENCY.labels(request.url.path).time():
            response = await call_next(request)
        REQUEST_COUNTER.labels(request.method, request.url.path, str(response.status_code)).inc()
        return response
    @app.get("/metrics")
    def metrics(): return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
