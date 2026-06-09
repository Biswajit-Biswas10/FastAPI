"""
monitoring.py - Application & Database Monitoring

Responsible for:
- Exposing Prometheus metrics at /metrics endpoint
- Tracking HTTP request latency, count, and error rate per endpoint
- Tracking database query count and latency
- Tracking active database connections
"""

import time
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge


# ── Application Metrics ──

# These are automatically handled by the Instrumentator,
# but we define custom ones for business-level tracking.

TODO_OPERATIONS = Counter(
    "todo_operations_total",
    "Total todo operations",
    ["operation"]  # create, read, update, delete
)

AUTH_EVENTS = Counter(
    "auth_events_total",
    "Total authentication events",
    ["event"]  # login_success, login_failed, registration
)

# ── Database Metrics ──

DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation"],  # select, insert, update, delete
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

DB_QUERY_COUNT = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation"]
)

ACTIVE_USERS = Gauge(
    "active_users_current",
    "Number of currently active users"
)

def setup_monitoring(app):
    """Attach Prometheus instrumentation to the FastAPI app."""
    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        excluded_handlers=["/healthy", "/metrics"],
    ).instrument(app).expose(app, endpoint="/metrics")


class DBMetricsTracker:
    """Context manager to track database query duration."""

    def __init__(self, operation: str):
        self.operation = operation

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start
        DB_QUERY_DURATION.labels(operation=self.operation).observe(duration)
        DB_QUERY_COUNT.labels(operation=self.operation).inc()

