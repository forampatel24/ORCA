"""Prometheus metrics - docs 18_MONITORING."""
from prometheus_client import Counter, Histogram, Gauge
import time

REQUEST_COUNT = Counter('orca_requests_total', 'Total requests', ['method','endpoint','status'])
REQUEST_DURATION = Histogram('orca_request_duration_seconds', 'Request duration', ['endpoint'])
AGENT_RUNS = Counter('orca_agent_runs_total', 'Agent runs', ['agent','status'])
ACTIVE_CONVERSATIONS = Gauge('orca_active_conversations', 'Active conversations')

def record_request(method: str, endpoint: str, status: int, duration: float):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    REQUEST_DURATION.labels(endpoint=endpoint).observe(duration)
