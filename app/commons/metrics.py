"""
Prometheus Metrics Export for Enterprise Observability

Provides comprehensive metrics collection and export for:
- HTTP request metrics (latency, status codes, throughput)
- ML inference metrics (prediction latency, confidence scores)
- Database query metrics
- System resource metrics
- Custom business metrics
"""

import time
from typing import Optional
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
import logging

logger = logging.getLogger(__name__)

# HTTP Request Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# ML Inference Metrics
ml_inference_requests_total = Counter(
    "ml_inference_requests_total",
    "Total ML inference requests",
    ["model_name", "model_version"],
)

ml_inference_duration_seconds = Histogram(
    "ml_inference_duration_seconds",
    "ML inference duration in seconds",
    ["model_name"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

ml_prediction_confidence = Histogram(
    "ml_prediction_confidence",
    "ML prediction confidence scores",
    ["model_name"],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)

ml_inference_errors_total = Counter(
    "ml_inference_errors_total",
    "Total ML inference errors",
    ["model_name", "error_type"],
)

# Database Metrics
db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

db_connections_active = Gauge(
    "db_connections_active",
    "Active database connections",
)

db_query_errors_total = Counter(
    "db_query_errors_total",
    "Total database query errors",
    ["operation", "error_type"],
)

# Circuit Breaker Metrics
circuit_breaker_state = Gauge(
    "circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 2=half-open)",
    ["service_name"],
)

circuit_breaker_failures_total = Counter(
    "circuit_breaker_failures_total",
    "Total circuit breaker failures",
    ["service_name"],
)

circuit_breaker_requests_rejected_total = Counter(
    "circuit_breaker_requests_rejected_total",
    "Total requests rejected by circuit breaker",
    ["service_name"],
)

# Rate Limiting Metrics
rate_limit_requests_total = Counter(
    "rate_limit_requests_total",
    "Total rate limit checks",
    ["endpoint", "result"],  # result: "allowed" or "rejected"
)

rate_limit_remaining = Gauge(
    "rate_limit_remaining",
    "Remaining rate limit quota",
    ["endpoint", "identifier"],
)

# System Metrics
system_memory_usage_bytes = Gauge(
    "system_memory_usage_bytes",
    "System memory usage in bytes",
)

system_cpu_usage_percent = Gauge(
    "system_cpu_usage_percent",
    "System CPU usage percentage",
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect HTTP request metrics for Prometheus.
    
    Automatically tracks:
    - Request count by method, endpoint, status code
    - Request duration (latency) by method, endpoint
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get endpoint path (normalize to avoid cardinality explosion)
        endpoint = self._normalize_path(request.url.path)
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=response.status_code,
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=endpoint,
        ).observe(duration)
        
        return response

    @staticmethod
    def _normalize_path(path: str) -> str:
        """
        Normalize path to avoid cardinality explosion.
        
        Replaces IDs and dynamic segments with placeholders.
        Example: /api/users/123 -> /api/users/{id}
        """
        # Simple normalization - replace numeric IDs
        import re
        path = re.sub(r"/\d+", "/{id}", path)
        # Replace UUIDs
        path = re.sub(
            r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "/{uuid}",
            path,
            flags=re.IGNORECASE,
        )
        return path


class MLMetricsCollector:
    """
    Collector for ML inference metrics.
    
    Usage:
        collector = MLMetricsCollector()
        with collector.record_inference("model_v1", "1.0.0"):
            result = model.predict(data)
        collector.record_confidence("model_v1", result.confidence)
    """

    def record_inference(
        self,
        model_name: str,
        model_version: str,
        duration: float,
        success: bool = True,
        error_type: Optional[str] = None,
    ):
        """Record ML inference metrics."""
        ml_inference_requests_total.labels(
            model_name=model_name,
            model_version=model_version,
        ).inc()
        
        ml_inference_duration_seconds.labels(model_name=model_name).observe(duration)
        
        if not success and error_type:
            ml_inference_errors_total.labels(
                model_name=model_name,
                error_type=error_type,
            ).inc()

    def record_confidence(self, model_name: str, confidence: float):
        """Record prediction confidence score."""
        ml_prediction_confidence.labels(model_name=model_name).observe(confidence)

    def record_inference_context(
        self,
        model_name: str,
        model_version: str,
        duration: float,
        confidence: Optional[float] = None,
        success: bool = True,
        error_type: Optional[str] = None,
    ):
        """Record complete inference context."""
        self.record_inference(model_name, model_version, duration, success, error_type)
        if confidence is not None:
            self.record_confidence(model_name, confidence)


def get_metrics_endpoint():
    """
    Create FastAPI endpoint handler for /metrics.
    
    Returns Prometheus metrics in text format.
    """
    async def metrics():
        return Response(
            content=generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST,
        )
    return metrics


# Singleton instance
ml_metrics = MLMetricsCollector()


