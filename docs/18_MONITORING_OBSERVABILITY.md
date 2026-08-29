# ORCA — Monitoring & Observability Architecture

**Project Name:** ORCA  
**Document:** Monitoring & Observability Architecture  
**Document ID:** ORCA-OBS-18  
**Version:** 1.0  
**Status:** FROZEN BASELINE

---

# 1. Purpose

This document defines how ORCA will monitor, observe, diagnose, and audit the complete system.

ORCA is a multi-agent platform involving:

- LLM APIs
- Multiple AI agents
- RAG
- PostgreSQL
- PostGIS
- Redis
- MinIO
- Qdrant
- External marine APIs
- Satellite/Earth Observation data
- Data ingestion pipelines
- Geospatial processing
- Analytics
- Routing
- Frontend visualization

Therefore, monitoring must allow the team to determine:

1. Whether the system is healthy.
2. Whether data is fresh.
3. Whether agents are functioning correctly.
4. Which agent failed.
5. Which tool failed.
6. Which external API failed.
7. How long a workflow took.
8. How much an LLM request cost.
9. Whether RAG retrieved useful evidence.
10. Whether a recommendation was properly supported.

---

# 2. Observability Philosophy

ORCA follows:

```text
Logs
+
Metrics
+
Traces
+
Audit Events
=
Complete Observability
````

Monitoring tells us:

```text
"Something is wrong."
```

Observability helps answer:

```text
"What happened?"
"Where did it happen?"
"Why did it happen?"
"What was the system doing?"
```

---

# 3. Three Pillars

ORCA uses the standard three observability pillars:

```text
                 OBSERVABILITY
                      |
          ┌───────────┼───────────┐
          ↓           ↓           ↓
        LOGS       METRICS      TRACES
```

Additionally:

```text
AUDIT EVENTS
```

will be used for security-sensitive and decision-related events.

---

# 4. Recommended Stack

Initial stack:

```text
Application Logging:
Python logging / structlog

Metrics:
Prometheus

Visualization:
Grafana

Distributed Tracing:
OpenTelemetry

Trace Storage:
Jaeger

Container Monitoring:
Docker

Database Monitoring:
PostgreSQL / PostGIS metrics

Cache Monitoring:
Redis metrics

Vector Database Monitoring:
Qdrant health + application metrics

Object Storage Monitoring:
MinIO health + metrics
```

---

# 5. Architecture

```text
                    ORCA
                     |
        ┌────────────┼────────────┐
        ↓            ↓            ↓
      Logs        Metrics       Traces
        |            |            |
        ↓            ↓            ↓
   Log System    Prometheus     Jaeger
                     |
                     ↓
                  Grafana
```

---

# 6. Request ID

Every user request should receive a unique:

```text
request_id
```

Example:

```text
REQ-8f73a2...
```

This identifier should be propagated through the complete workflow.

---

# 7. Task ID

Complex agentic workflows should additionally receive:

```text
task_id
```

Example:

```text
TASK-91bc...
```

One request can therefore contain multiple internal tasks.

---

# 8. Agent Execution ID

Every agent execution should have:

```text
agent_run_id
```

Example:

```text
AGENTRUN-45ad...
```

This allows individual agent execution to be investigated.

---

# 9. Trace ID

OpenTelemetry should provide:

```text
trace_id
```

A trace represents the complete execution of a workflow.

Example:

```text
User Request
     |
     └── Trace ID
           |
           ├── Planner
           ├── Weather Agent
           ├── Ocean Agent
           ├── Geo Agent
           ├── Risk Agent
           └── Response Agent
```

---

# 10. Span

Each major operation should generate a span.

Example:

```text
Trace
 |
 ├── Intent Detection
 ├── Planning
 ├── Weather Retrieval
 ├── Ocean Retrieval
 ├── Geospatial Query
 ├── Risk Calculation
 ├── RAG Retrieval
 └── Final Response
```

---

# 11. Structured Logging

Logs should use structured fields.

Example:

```json
{
  "timestamp": "...",
  "level": "INFO",
  "service": "risk-agent",
  "request_id": "...",
  "task_id": "...",
  "agent_run_id": "...",
  "event": "risk_calculation_completed",
  "risk_level": "HIGH"
}
```

Logs should not depend only on free-form text.

---

# 12. Log Levels

Use:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

---

# 13. DEBUG

Used for development diagnostics.

Examples:

```text
Tool parameters
Intermediate processing
Cache decisions
Retrieval details
```

DEBUG logs should not expose secrets.

---

# 14. INFO

Normal system events.

Examples:

```text
Request received
Agent started
Agent completed
Dataset ingestion completed
Cache hit
Cache miss
```

---

# 15. WARNING

Potential problems that do not necessarily stop execution.

Examples:

```text
Stale dataset
Slow API
Missing optional field
Fallback data source
Agent retry
```

---

# 16. ERROR

An operation failed.

Examples:

```text
External API failure
Database query failure
Agent tool failure
RAG retrieval failure
Invalid data
```

---

# 17. CRITICAL

System-threatening failures.

Examples:

```text
Database unavailable
Authentication infrastructure failure
Data corruption
Critical safety pipeline failure
```

---

# 18. Never Log

Never log:

```text
API keys
Passwords
JWT secrets
Database credentials
Private tokens
Sensitive user information
```

---

# 19. Request Metrics

Track:

```text
requests_total
requests_success_total
requests_failed_total
request_duration_seconds
```

---

# 20. API Metrics

For each API:

```text
request count
success count
error count
latency
status code
```

Example:

```text
GET /api/v1/weather
```

Metrics should distinguish:

```text
200
400
401
404
429
500
```

where appropriate.

---

# 21. Agent Metrics

Each agent should expose metrics such as:

```text
agent_runs_total
agent_success_total
agent_failure_total
agent_duration_seconds
agent_retry_total
```

---

# 22. Agent-Specific Metrics

Track individual agents:

```text
planner
weather
ocean
geospatial
risk
routing
rag
visualization
reporting
```

This allows comparison of agent behavior.

---

# 23. Agent Failure Rate

Calculate:

```text
failure rate =
failed executions / total executions
```

This helps identify unstable agents.

---

# 24. Agent Retry Metrics

Track:

```text
retry count
retry reason
retry success
retry failure
```

Excessive retries indicate an architectural or integration problem.

---

# 25. Agent Loop Monitoring

Track:

```text
agent calls per task
maximum depth
number of replans
number of tool calls
```

If execution exceeds configured limits:

```text
STOP
```

and record the reason.

---

# 26. Tool Metrics

Every agent tool invocation should record:

```text
tool name
agent
duration
success
failure
```

Example:

```text
weather_api
postgis_query
qdrant_search
minio_download
route_engine
```

---

# 27. Tool Error Metrics

Track errors by:

```text
tool
error type
HTTP status
timeout
dependency
```

---

# 28. LLM Metrics

Track:

```text
LLM requests
successful requests
failed requests
latency
input tokens
output tokens
total tokens
```

---

# 29. LLM Model Tracking

Every LLM request should record the model identifier used.

Example:

```text
model_name
model_version
provider
```

This enables comparison when models change.

---

# 30. LLM Cost Monitoring

Where pricing information is available, calculate:

```text
estimated request cost
daily cost
weekly cost
monthly cost
```

The system should not assume that all LLM calls have identical costs.

---

# 31. Token Monitoring

Track:

```text
input_tokens
output_tokens
total_tokens
```

This helps detect unnecessarily large prompts.

---

# 32. RAG Metrics

Track:

```text
retrieval_count
retrieval_latency
documents_retrieved
chunks_retrieved
empty_retrievals
```

---

# 33. RAG Quality Metrics

Where evaluation infrastructure exists:

```text
precision@k
recall@k
MRR
NDCG
groundedness
citation correctness
```

These belong primarily to evaluation rather than real-time operational monitoring.

---

# 34. RAG Failure Monitoring

Important event:

```text
retrieval_empty
```

This means the system found no suitable evidence.

ORCA should not silently generate an answer as though evidence existed.

---

# 35. Evidence Monitoring

Track whether a final recommendation has:

```text
supporting evidence
source
timestamp
dataset
```

---

# 36. Recommendation Audit

For important recommendations, store an audit representation containing:

```text
request_id
task_id
input context
data sources
observations
analytical outputs
risk result
recommendation
timestamp
```

Do not store unnecessary sensitive information.

---

# 37. Data Pipeline Monitoring

Every ingestion pipeline should expose:

```text
pipeline_runs_total
pipeline_success_total
pipeline_failure_total
pipeline_duration
records_received
records_valid
records_rejected
```

---

# 38. Dataset Freshness

Each important dataset should have:

```text
last_successful_update
data_timestamp
ingestion_timestamp
freshness_status
```

---

# 39. Freshness Status

Possible states:

```text
FRESH
AGING
STALE
UNAVAILABLE
```

Thresholds must be defined according to the dataset.

---

# 40. Dataset Failure

If a dataset cannot be updated:

```text
ingestion_failed
```

should be recorded.

The system should distinguish:

```text
Latest data unavailable
```

from:

```text
No data exists
```

---

# 41. Data Quality Metrics

Track:

```text
null percentage
invalid record count
duplicate count
invalid geometry count
invalid timestamp count
```

---

# 42. PostgreSQL Monitoring

Monitor:

```text
connection count
query latency
active connections
failed queries
database size
transaction activity
```

---

# 43. PostGIS Monitoring

Monitor important geospatial queries for:

```text
execution time
rows processed
query failures
spatial index usage
```

---

# 44. Slow Query Monitoring

Identify queries exceeding a configured threshold.

Example:

```text
PostGIS query > configured latency
→ WARNING
```

---

# 45. Redis Monitoring

Monitor:

```text
cache hit rate
cache miss rate
memory usage
key count
connection errors
```

---

# 46. Redis Health

If Redis becomes unavailable:

```text
Application
     |
     ↓
Cache unavailable
     |
     ↓
Fallback to primary source
```

where the architecture permits it.

---

# 47. Qdrant Monitoring

Monitor:

```text
collection availability
search latency
insert latency
collection size
failed searches
```

---

# 48. MinIO Monitoring

Monitor:

```text
storage availability
object operations
failed uploads
failed downloads
storage usage
```

---

# 49. External API Monitoring

For each external API:

```text
availability
latency
error rate
rate-limit responses
timeouts
```

---

# 50. External API Health

Maintain a dependency health view:

```text
Weather API       HEALTHY
Ocean API         HEALTHY
Satellite source  DEGRADED
Routing source    HEALTHY
```

The exact dependencies depend on the final integration set.

---

# 51. Dependency Health

ORCA should expose a health endpoint such as:

```text
/health
```

for basic application health.

---

# 52. Readiness

A separate readiness concept should indicate whether the service is ready to accept traffic.

Conceptually:

```text
Liveness:
"Is the process alive?"

Readiness:
"Can the service actually operate?"
```

---

# 53. Liveness Checks

Check that:

```text
Backend process
Agent service
Worker
```

are running.

---

# 54. Readiness Checks

Check required dependencies according to service requirements:

```text
PostgreSQL
Redis
Qdrant
MinIO
```

External APIs may be monitored separately rather than making readiness depend on every third-party service.

---

# 55. Container Health

Docker containers should have health checks where appropriate.

Example:

```text
Container
 ↓
Health Check
 ↓
healthy / unhealthy
```

---

# 56. Grafana Dashboards

ORCA should eventually maintain dashboards for:

```text
1. System Overview
2. API Performance
3. Agent Performance
4. LLM Usage
5. RAG
6. Data Pipelines
7. Database
8. External APIs
9. Security
10. Infrastructure
```

---

# 57. System Overview Dashboard

Display:

```text
Requests/min
Error rate
Average latency
Active tasks
Agent failures
External dependency status
```

---

# 58. Agent Dashboard

Display:

```text
Runs
Success rate
Failure rate
Latency
Retries
Tool calls
```

per agent.

---

# 59. LLM Dashboard

Display:

```text
Requests
Tokens
Latency
Failures
Model usage
Estimated cost
```

---

# 60. RAG Dashboard

Display:

```text
Retrieval count
Retrieval latency
Empty retrieval rate
Documents retrieved
Evaluation metrics
```

where applicable.

---

# 61. Data Dashboard

Display:

```text
Dataset freshness
Pipeline status
Records processed
Rejected records
Last successful ingestion
```

---

# 62. Database Dashboard

Display:

```text
Connections
Query latency
Database size
Errors
Slow queries
```

---

# 63. External Dependency Dashboard

Display:

```text
API
Status
Latency
Error rate
Last successful request
Rate-limit events
```

---

# 64. Alerting

Alerts should exist for important operational failures.

Examples:

```text
High API error rate
Database unavailable
External API unavailable
Data pipeline failure
Dataset stale
High agent failure rate
LLM API failure
High Redis memory
Qdrant unavailable
MinIO unavailable
```

---

# 65. Alert Severity

Use:

```text
INFO
WARNING
CRITICAL
```

---

# 66. Safety-Relevant Alerting

Special attention should be given to:

```text
Marine data unavailable
Hazard data unavailable
Geofence service unavailable
Risk engine failure
```

These failures should be visible and should influence system behavior.

---

# 67. Fail-Safe Behavior

If critical safety information is unavailable:

```text
Do not fabricate information.
```

Instead:

```text
Data unavailable
+
Explain limitation
+
Avoid unsupported safety recommendation
```

---

# 68. Trace Example

A complete user request might produce:

```text
TRACE-001
|
├── Intent Detection
|
├── Planner
|    |
|    ├── Weather API
|    ├── Ocean API
|    └── Geospatial Query
|
├── Risk Agent
|
├── RAG Retrieval
|
└── Response Generation
```

This allows the complete execution chain to be inspected.

---

# 69. Trace Context Propagation

The following identifiers should be propagated where relevant:

```text
trace_id
span_id
request_id
task_id
agent_run_id
```

---

# 70. Error Correlation

When an error occurs, logs should allow engineers to move from:

```text
Error
 ↓
Request
 ↓
Trace
 ↓
Agent
 ↓
Tool
 ↓
Dependency
```

---

# 71. Example Diagnostic Scenario

User receives:

```text
"Marine risk could not be determined."
```

Engineering team should be able to inspect:

```text
Request
 ↓
Risk Agent
 ↓
Ocean Tool
 ↓
Ocean API
 ↓
HTTP 503
```

rather than debugging blindly.

---

# 72. Agent Decision Observability

For agentic execution, record structured metadata such as:

```text
agent
task
selected tool
tool result status
replan event
completion status
```

Do not rely on storing hidden/internal model reasoning.

---

# 73. Explainability Logging

Store the factual evidence used for a recommendation.

Example:

```text
Sea state: High
Wind: Strong
Cyclone warning: Active
Restricted area: No
```

Then:

```text
Recommendation:
Avoid fishing.
```

---

# 74. No Hidden Chain-of-Thought Storage

ORCA should not depend on storing private chain-of-thought.

Instead store:

```text
Inputs
Evidence
Tool calls
Calculated outputs
Decision factors
Final recommendation
```

---

# 75. Security Monitoring

Monitor:

```text
Failed logins
Repeated authorization failures
Rate-limit violations
Suspicious requests
Prompt injection attempts
Malicious uploads
```

---

# 76. Authentication Monitoring

Track:

```text
login success
login failure
token validation failure
logout
```

without logging credentials.

---

# 77. Audit Logging

Security-sensitive events should generate audit events.

Examples:

```text
User login
Permission change
Sensitive configuration change
Dataset modification
Administrative operation
```

---

# 78. Log Retention

Retention policies should distinguish:

```text
Application logs
Security logs
Audit logs
Metrics
Traces
```

Retention should be chosen based on:

```text
Storage capacity
Security requirements
Operational needs
Privacy requirements
```

---

# 79. Development vs Production

Development may use:

```text
Verbose logs
Local Grafana
Local Prometheus
Local Jaeger
```

Production should use:

```text
Structured logs
Controlled retention
Authentication
Restricted dashboards
```

---

# 80. Monitoring Environment

Local architecture:

```text
Docker
 |
 ├── ORCA Backend
 ├── PostgreSQL/PostGIS
 ├── Redis
 ├── Qdrant
 ├── MinIO
 ├── Prometheus
 ├── Grafana
 └── Jaeger
```

The exact deployment arrangement can evolve without changing the observability principles.

---

# 81. Monitoring Configuration

Monitoring configuration should be environment-specific.

Example:

```text
.env
.env.development
.env.production
```

Secrets must never be committed.

---

# 82. Metrics Naming

Metrics should follow consistent names.

Examples:

```text
orca_requests_total
orca_request_duration_seconds
orca_agent_runs_total
orca_agent_duration_seconds
orca_rag_search_duration_seconds
orca_pipeline_runs_total
```

---

# 83. Labels

Metrics can include controlled labels such as:

```text
service
agent
endpoint
status
dataset
```

Avoid extremely high-cardinality labels.

Do not use:

```text
user_id
request_id
trace_id
```

as unrestricted metric labels.

These belong in logs/traces.

---

# 84. High Cardinality Protection

Do not create metrics with millions of unique label values.

Use:

```text
Metrics → aggregation
Logs → individual events
Traces → request-level detail
```

---

# 85. Monitoring Data Flow

```text
ORCA Services
     |
     ├── Logs ─────→ Logging system
     |
     ├── Metrics ───→ Prometheus
     |
     └── Traces ────→ OpenTelemetry
                         |
                         ↓
                       Jaeger

Prometheus
     |
     ↓
Grafana

Jaeger
     |
     ↓
Trace Investigation
```

---

# 86. Operational Workflow

When an issue is detected:

```text
1. Check Grafana
2. Identify abnormal metric
3. Find affected service
4. Open trace
5. Inspect spans
6. Inspect structured logs
7. Identify failing dependency
8. Fix
9. Run regression tests
10. Deploy
11. Verify recovery
```

---

# 87. Incident Example

Problem:

```text
Risk requests suddenly fail.
```

Investigation:

```text
Grafana
 ↓
Risk Agent failure rate ↑
 ↓
Trace
 ↓
Ocean Tool failing
 ↓
External Ocean API timeout
```

This provides a complete diagnostic path.

---

# 88. Data Freshness Incident

Problem:

```text
Marine observations are stale.
```

Investigation:

```text
Dataset dashboard
 ↓
Last ingestion = old
 ↓
Pipeline logs
 ↓
Download failed
 ↓
External source unavailable
```

---

# 89. Agent Incident

Problem:

```text
Planner is taking too long.
```

Investigation:

```text
Agent dashboard
 ↓
Planner latency ↑
 ↓
Trace
 ↓
Repeated tool calls
 ↓
Replanning loop
```

---

# 90. Cost Incident

Problem:

```text
LLM cost unexpectedly increases.
```

Investigation:

```text
LLM dashboard
 ↓
Token usage ↑
 ↓
Planner token count ↑
 ↓
Prompt/context increased
```

---

# 91. Monitoring Tests

Monitoring itself must be tested.

Verify:

```text
Logs generated
Metrics generated
Trace generated
Correlation IDs propagated
Alerts triggered
Health endpoints work
```

---

# 92. Alert Tests

Alerts should be tested using controlled failures.

Example:

```text
Stop Redis
 ↓
Redis health alert
```

Then:

```text
Restore Redis
 ↓
Recovery observed
```

---

# 93. Recovery Monitoring

The monitoring system should show:

```text
DEGRADED
 ↓
RECOVERING
 ↓
HEALTHY
```

where such states are implemented.

---

# 94. Observability Acceptance Criteria

ORCA should allow engineers to answer:

```text
What request failed?
Which agent failed?
Which tool failed?
Which external API failed?
How long did the request take?
What data was retrieved?
Was the data stale?
What evidence supported the result?
How many LLM calls occurred?
How many tokens were consumed?
```

---

# 95. Critical Observability Requirements

The following are mandatory:

1. Request IDs.
2. Task IDs.
3. Structured logs.
4. Agent execution tracking.
5. Tool execution tracking.
6. API health monitoring.
7. Database health monitoring.
8. Dataset freshness monitoring.
9. RAG monitoring.
10. LLM usage monitoring.
11. Error tracking.
12. Distributed tracing for important workflows.
13. Safety-data availability monitoring.
14. Audit events for important operations.
15. No secret exposure.
16. Fail-safe behavior for unavailable critical data.

---

# 96. Frozen Monitoring Principles

ORCA officially follows:

1. Every important request must be traceable.
2. Every agent execution must be observable.
3. Every tool call must be measurable.
4. Important external dependencies must be monitored.
5. Dataset freshness must be visible.
6. Critical data failures must not be hidden.
7. Safety-relevant failures must be treated specially.
8. LLM usage must be measurable.
9. RAG retrieval must be observable.
10. Geospatial operations must be diagnosable.
11. Logs must be structured.
12. Metrics must remain low-cardinality.
13. Traces must connect multi-agent workflows.
14. Secrets must never appear in logs.
15. Monitoring must distinguish failure from missing data.
16. Monitoring must support incident diagnosis.
17. Recovery must be observable.
18. Agent execution must be auditable without storing private chain-of-thought.
19. Monitoring must support development and production environments.
20. Observability must cover the complete ORCA decision pipeline.

---

# 97. Final Observability Model

```text
                         USER
                           |
                           ↓
                     ORCA REQUEST
                           |
                       request_id
                           |
                       task_id
                           |
                       trace_id
                           |
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
      AGENTS             TOOLS             DATA
        |                  |                  |
        ↓                  ↓                  ↓
      Metrics            Metrics            Freshness
      Logs               Logs               Quality
      Traces             Traces             Pipeline
        |                  |                  |
        └──────────────────┼──────────────────┘
                           ↓
                     DECISION ENGINE
                           |
                           ↓
                      RECOMMENDATION
                           |
                           ↓
                    EVIDENCE + OUTPUT
                           |
                           ↓
                    OBSERVABILITY
                           |
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
          Grafana       Prometheus      Jaeger
```

---

# 98. Status

This document freezes the baseline observability architecture for ORCA.

Future implementation may refine:

* Exact metric names
* Alert thresholds
* Dashboard layouts
* Log storage
* Retention periods
* Production infrastructure

without changing the core observability architecture.
