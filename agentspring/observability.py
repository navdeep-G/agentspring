# agentspring/observability.py
from __future__ import annotations
import os
import logging
from .config import settings


def setup_logging():
    level_name = (settings.LOG_LEVEL or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def setup_sentry():
    dsn = getattr(settings, "SENTRY_DSN", None)
    if not dsn:
        return
    try:
        import sentry_sdk  # type: ignore
        traces_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0"))
        sentry_sdk.init(dsn=dsn, traces_sample_rate=traces_rate)
    except Exception as e:  # noqa: BLE001
        logging.getLogger(__name__).warning("Sentry init failed: %s", e)


def setup_tracing(service_name: str):
    endpoint = getattr(settings, "OTEL_EXPORTER_OTLP_ENDPOINT", None)
    if not endpoint:
        return
    try:
        from opentelemetry import trace  # type: ignore
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # type: ignore
        from opentelemetry.sdk.resources import Resource  # type: ignore
        from opentelemetry.sdk.trace import TracerProvider  # type: ignore
        from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore

        headers = getattr(settings, "OTEL_EXPORTER_OTLP_HEADERS", None)
        exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)

        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
    except Exception as e:  # noqa: BLE001
        logging.getLogger(__name__).warning("OTEL init failed: %s", e)

