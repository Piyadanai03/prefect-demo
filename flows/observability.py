import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

logger = logging.getLogger(__name__)


def setup_telemetry(service_name: str = "prefect-worker"):
    """ตั้งค่า OpenTelemetry สำหรับส่ง traces ไป Tempo."""
    try:
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        
        resource = Resource.create({
            "service.name": service_name,
            "deployment.environment": "production",
        })
        
        provider = TracerProvider(resource=resource)
        
        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=True,
        )
        
        processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(processor)
        
        trace.set_tracer_provider(provider)
        
        SQLAlchemyInstrumentor().instrument()
        LoggingInstrumentor().instrument(set_logging_format=True)
        
        logger.info(
            "✅ OpenTelemetry initialized: service=%s, endpoint=%s",
            service_name,
            otlp_endpoint,
        )
    except Exception as e:
        logger.warning("⚠️ Failed to initialize OpenTelemetry: %s", e)


def get_tracer(name: str = __name__):
    """ดึง tracer สำหรับสร้าง custom spans."""
    return trace.get_tracer(name)