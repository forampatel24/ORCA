# ORCA — API Specification

**Project Name:** ORCA  
**Document:** API Specification  
**Document ID:** ORCA-API-12  
**Version:** 1.0  
**Status:** FROZEN BASELINE  
**Scope:** Backend API, Agent APIs, Tool APIs, Database Access, Streaming, Errors, Authentication and Frontend Integration

---

# 1. Purpose

The ORCA API layer provides the communication interface between:

- Frontend
- Orchestrator
- AI Agents
- Data services
- Databases
- External APIs
- Visualization layer

The backend will expose REST APIs through FastAPI.

---

# 2. API Architecture

```text
                         FRONTEND
                            │
                            ▼
                         FASTAPI
                            │
                     API ROUTER LAYER
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          Chat API      Data API      Map API
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                      ORCHESTRATOR
                            │
            ┌───────────────┼────────────────┐
            ▼               ▼                ▼
         AGENTS           TOOLS           SERVICES
            │               │                │
            └───────────────┼────────────────┘
                            ▼
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         PostgreSQL       PostGIS        Qdrant
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                           MinIO
                            +
                          Redis
````

---

# 3. API Technology

Primary backend:

```text
FastAPI
Python
Pydantic
Uvicorn
SQLAlchemy
Async database access where appropriate
```

---

# 4. API Versioning

All public APIs should be versioned.

Base path:

```text
/api/v1
```

Example:

```text
/api/v1/chat
/api/v1/pfz
/api/v1/weather
/api/v1/ocean
/api/v1/maps
```

---

# 5. API Categories

The API will contain:

```text
1. Health APIs
2. Authentication APIs
3. Chat APIs
4. Conversation APIs
5. Agent APIs
6. PFZ APIs
7. Weather APIs
8. Ocean APIs
9. Hazard APIs
10. Geospatial APIs
11. Risk APIs
12. Routing APIs
13. RAG APIs
14. Visualization APIs
15. Reporting APIs
16. Dataset APIs
```

---

# 6. Health API

## GET `/api/v1/health`

Purpose:

Check whether the ORCA backend is running.

Response:

```json
{
  "status": "healthy",
  "service": "orca-api",
  "version": "1.0.0"
}
```

---

# 7. Detailed Health API

## GET `/api/v1/health/services`

Checks important dependencies.

Conceptually:

```json
{
  "api": "healthy",
  "postgresql": "healthy",
  "postgis": "healthy",
  "qdrant": "healthy",
  "redis": "healthy",
  "minio": "healthy"
}
```

The exact implementation may report unavailable services separately.

---

# 8. Chat API

The primary user-facing API is:

```text
POST /api/v1/chat
```

Purpose:

Accept a natural-language marine intelligence query.

---

# 9. Chat Request

Example:

```json
{
  "message": "Is it safe to fish tomorrow morning?",
  "conversation_id": "optional-id",
  "location": {
    "latitude": 18.5204,
    "longitude": 73.8567
  },
  "language": "auto"
}
```

---

# 10. Chat Response

Conceptually:

```json
{
  "conversation_id": "...",
  "response": "...",
  "language": "en",
  "request_id": "...",
  "evidence": [],
  "visualizations": [],
  "risk": null,
  "sources": []
}
```

The exact schema should be implemented through Pydantic models.

---

# 11. Chat Execution Flow

```text
POST /chat
      │
      ▼
Validate Request
      │
      ▼
Language Detection
      │
      ▼
Intent Understanding
      │
      ▼
Orchestrator
      │
      ▼
Task Planning
      │
      ▼
Agent Execution
      │
      ▼
Evidence Aggregation
      │
      ▼
Final LLM
      │
      ▼
Response
```

---

# 12. Streaming Chat

For long-running agentic requests, streaming should be supported.

Example:

```text
POST /api/v1/chat/stream
```

Conceptually:

```text
User Query
   ↓
Planning
   ↓
Agent execution
   ↓
Results
   ↓
Final response
```

The frontend can receive progress events.

---

# 13. Streaming Events

Possible events:

```text
request_started
planning_started
task_created
agent_started
tool_called
tool_completed
agent_completed
replanning
risk_calculated
visualization_ready
response_ready
request_completed
error
```

---

# 14. Conversation API

## POST `/api/v1/conversations`

Creates a conversation.

Response:

```json
{
  "conversation_id": "...",
  "created_at": "..."
}
```

---

# 15. Conversation History

## GET `/api/v1/conversations/{conversation_id}`

Returns conversation state and relevant history.

---

# 16. Delete Conversation

## DELETE `/api/v1/conversations/{conversation_id}`

Deletes the conversation according to the application's retention policy.

---

# 17. Agent Execution API

Internal agent execution should remain separate from public chat APIs.

Conceptually:

```text
/api/v1/internal/agents/{agent_name}
```

These endpoints are primarily for service-level integration and testing.

The frontend should normally communicate with `/chat`, not directly control agents.

---

# 18. Agent Task Schema

Conceptually:

```json
{
  "task_id": "...",
  "agent": "weather_agent",
  "objective": "Retrieve tomorrow morning weather conditions",
  "inputs": {},
  "priority": "normal"
}
```

---

# 19. Agent Result Schema

```json
{
  "task_id": "...",
  "agent": "weather_agent",
  "status": "completed",
  "data": {},
  "sources": [],
  "timestamp": "..."
}
```

---

# 20. PFZ API

## GET `/api/v1/pfz`

Retrieves PFZ information.

Supported parameters may include:

```text
latitude
longitude
radius
date
limit
```

---

# 21. Nearest PFZ

## GET `/api/v1/pfz/nearest`

Purpose:

Find the nearest relevant PFZ to a coordinate.

Example parameters:

```text
latitude
longitude
date
radius
```

Spatial calculations should be performed using PostGIS.

---

# 22. PFZ Response

Conceptually:

```json
{
  "results": [
    {
      "pfz_id": "...",
      "latitude": 18.42,
      "longitude": 72.91,
      "distance_km": 14.7,
      "date": "..."
    }
  ]
}
```

---

# 23. Weather API

## GET `/api/v1/weather`

Parameters may include:

```text
latitude
longitude
start_time
end_time
```

Response should contain structured weather information.

Possible fields:

```text
temperature
wind_speed
wind_direction
rainfall
pressure
visibility
weather_condition
timestamp
source
```

---

# 24. Ocean API

## GET `/api/v1/ocean`

Used for oceanographic information.

Possible parameters:

```text
latitude
longitude
start_time
end_time
variables
```

Possible variables:

```text
SST
chlorophyll
wave_height
wave_period
currents
```

---

# 25. Tide API

## GET `/api/v1/tides`

Returns tidal information for the requested location and time range.

---

# 26. Hazard API

## GET `/api/v1/hazards`

Returns relevant marine hazards.

Possible hazard types:

```text
lightning
cyclone
high_waves
strong_wind
heavy_rain
low_visibility
marine_advisory
```

---

# 27. Hazard Query

Example:

```text
GET /api/v1/hazards?latitude=...&longitude=...&start_time=...&end_time=...
```

---

# 28. Geospatial API

## POST `/api/v1/geospatial/query`

Used for spatial analysis.

Potential operations:

```text
nearest
within_radius
intersects
contains
distance
geofence
```

---

# 29. Geofence API

## POST `/api/v1/geospatial/geofence/check`

Input:

```json
{
  "latitude": 18.52,
  "longitude": 72.88
}
```

Output:

```json
{
  "inside_restricted_area": false,
  "inside_marine_protected_area": false,
  "boundaries": []
}
```

---

# 30. Route API

## POST `/api/v1/routes/calculate`

Input:

```json
{
  "origin": {
    "latitude": 18.50,
    "longitude": 72.80
  },
  "destination": {
    "latitude": 18.70,
    "longitude": 73.10
  }
}
```

---

# 31. Route Response

Conceptually:

```json
{
  "routes": [
    {
      "route_id": "...",
      "distance_km": 42.3,
      "duration": "...",
      "risk_score": 0.24,
      "geofence_violations": [],
      "hazards": []
    }
  ]
}
```

---

# 32. Route Optimization

## POST `/api/v1/routes/optimize`

The API should support criteria such as:

```text
minimum risk
minimum distance
minimum travel time
balanced score
```

The final implementation should use deterministic route scoring rather than asking an LLM to calculate route geometry.

---

# 33. Risk API

## POST `/api/v1/risk/assess`

Input:

```json
{
  "location": {
    "latitude": 18.52,
    "longitude": 72.88
  },
  "time_range": {
    "start": "...",
    "end": "..."
  },
  "conditions": {}
}
```

---

# 34. Risk Response

```json
{
  "risk_score": 0.72,
  "risk_level": "high",
  "factors": [
    {
      "factor": "wave_height",
      "contribution": 0.31
    },
    {
      "factor": "wind_speed",
      "contribution": 0.22
    }
  ],
  "timestamp": "..."
}
```

The exact scoring model is defined by the Risk Engine.

---

# 35. RAG API

## POST `/api/v1/knowledge/search`

Purpose:

Search the ORCA knowledge base.

Input:

```json
{
  "query": "marine fishing safety regulations",
  "language": "en",
  "top_k": 10,
  "filters": {
    "region": "India"
  }
}
```

---

# 36. RAG Response

```json
{
  "results": [
    {
      "document_id": "...",
      "chunk_id": "...",
      "title": "...",
      "text": "...",
      "page": 12,
      "score": 0.91,
      "source": "...",
      "trust_level": "official"
    }
  ]
}
```

---

# 37. Document Ingestion API

## POST `/api/v1/knowledge/documents`

Used by authorized ingestion workflows.

Supported document types:

```text
PDF
DOCX
TXT
HTML
Markdown
```

The API should validate file type and size before processing.

---

# 38. Document Processing

```text
Upload
  ↓
Validation
  ↓
MinIO
  ↓
Text Extraction
  ↓
Cleaning
  ↓
Chunking
  ↓
Embeddings
  ↓
Qdrant
```

---

# 39. Visualization API

## POST `/api/v1/visualizations`

Creates a visualization specification.

Possible types:

```text
map
heatmap
line_chart
scatter_plot
bar_chart
risk_layer
route_map
PFZ_map
```

---

# 40. Visualization Response

Conceptually:

```json
{
  "visualization_id": "...",
  "type": "map",
  "data": {},
  "layers": [],
  "center": {},
  "zoom": 7
}
```

---

# 41. Map Layers

The frontend should be able to render layers such as:

```text
PFZ
SST
Chlorophyll
Weather
Waves
Hazards
Protected Areas
Geofences
Routes
```

---

# 42. Reporting API

## POST `/api/v1/reports`

Creates a structured marine intelligence report.

Possible report types:

```text
Safety Report
Fishing Intelligence Report
Route Report
Ocean Analysis Report
Hazard Report
```

---

# 43. Dataset API

Internal APIs may expose normalized dataset information.

Example:

```text
GET /api/v1/datasets
GET /api/v1/datasets/{dataset_id}
```

These APIs are primarily for administration and observability.

---

# 44. Database Access Boundary

The frontend must NOT directly access:

```text
PostgreSQL
PostGIS
Qdrant
Redis
MinIO
```

Instead:

```text
Frontend
   ↓
FastAPI
   ↓
Service Layer
   ↓
Database
```

---

# 45. PostgreSQL Access

Application services access PostgreSQL through:

```text
SQLAlchemy
```

Responsibilities:

```text
Users
Conversations
Requests
Metadata
Structured marine records
Agent execution records
```

---

# 46. PostGIS Access

PostGIS should handle:

```text
Coordinate queries
Distance
Nearest-neighbour search
Spatial intersections
Geofencing
Protected-area queries
Route geometry operations
```

---

# 47. Qdrant Access

Only the RAG service should normally communicate directly with Qdrant.

```text
RAG Agent
   ↓
RAG Service
   ↓
Qdrant
```

---

# 48. MinIO Access

The document/data service communicates with MinIO.

```text
Ingestion Service
       ↓
     MinIO
```

Original documents should not be exposed directly through arbitrary public URLs.

---

# 49. Redis Access

Redis can be used for:

```text
Caching
Session state
Temporary task state
Rate limiting
Short-lived results
```

---

# 50. Authentication

Protected APIs should require authentication.

Conceptually:

```text
User
 ↓
Login
 ↓
Access Token
 ↓
FastAPI
 ↓
Authorization
```

JWT-based authentication can be used.

---

# 51. Authorization

Different operations may require different permissions.

Example:

```text
USER
→ Chat
→ View data
→ View maps

ADMIN
→ Upload knowledge
→ Manage datasets
→ Manage system configuration
```

---

# 52. API Security

The backend should implement:

```text
Input validation
Authentication
Authorization
Rate limiting
File validation
Request size limits
CORS policy
Secret management
```

---

# 53. CORS

During development:

```text
Frontend
localhost
        ↓
FastAPI
localhost
```

Production should use an explicit allowed-origin list.

Wildcard origins should not be used unnecessarily.

---

# 54. Error Format

All APIs should return a consistent error structure.

Example:

```json
{
  "error": {
    "code": "INVALID_LOCATION",
    "message": "The supplied coordinates are invalid.",
    "request_id": "..."
  }
}
```

---

# 55. HTTP Status Codes

Common codes:

```text
200 OK
201 Created
202 Accepted
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
429 Too Many Requests
500 Internal Server Error
502 External Service Error
503 Service Unavailable
504 Gateway Timeout
```

---

# 56. Request IDs

Every request should receive a unique request ID.

Example:

```text
X-Request-ID
```

This enables tracing across:

```text
API
 ↓
Orchestrator
 ↓
Agents
 ↓
Tools
 ↓
Databases
```

---

# 57. Agent Task IDs

Every agent task should have a task ID.

Example:

```text
request_id:
REQ-123

task_id:
TASK-456
```

---

# 58. Logging

Backend logs should include:

```text
request_id
task_id
agent
tool
status
latency
error
```

Sensitive information should not be logged unnecessarily.

---

# 59. API Observability

The API layer should track:

```text
Request count
Latency
Error rate
Agent execution time
Tool execution time
Database latency
LLM latency
```

---

# 60. Async Execution

Long-running operations should not block the API unnecessarily.

Examples:

```text
Document ingestion
Large dataset processing
Complex route analysis
Multi-agent analysis
Report generation
```

These can use asynchronous/background execution architecture.

---

# 61. Idempotency

Operations that create expensive or duplicate resources should support idempotency where appropriate.

Example:

```text
Document ingestion
Report generation
Long-running analysis
```

---

# 62. API Request Validation

Pydantic models should validate:

```text
Coordinates
Dates
Time ranges
Enums
Numeric ranges
Required fields
Optional fields
```

---

# 63. Coordinate Validation

Latitude:

```text
-90 ≤ latitude ≤ 90
```

Longitude:

```text
-180 ≤ longitude ≤ 180
```

Invalid coordinates must be rejected.

---

# 64. Time Validation

The backend should normalize timestamps.

Internally:

```text
UTC
```

User-facing responses may be converted to the user's relevant timezone.

---

# 65. API Layer Structure

Recommended backend structure:

```text
backend/
└── app/
    ├── main.py
    │
    ├── api/
    │   └── v1/
    │       ├── chat.py
    │       ├── conversations.py
    │       ├── pfz.py
    │       ├── weather.py
    │       ├── ocean.py
    │       ├── hazards.py
    │       ├── geospatial.py
    │       ├── routes.py
    │       ├── risk.py
    │       ├── knowledge.py
    │       ├── visualization.py
    │       └── reports.py
    │
    ├── agents/
    ├── services/
    ├── tools/
    ├── models/
    ├── schemas/
    ├── repositories/
    ├── core/
    └── utils/
```

---

# 66. Separation of Responsibilities

The API layer should NOT contain business logic.

Bad:

```text
API endpoint
   ↓
500 lines of logic
```

Preferred:

```text
API
 ↓
Service
 ↓
Repository / Agent / Tool
```

---

# 67. Service Layer

Example:

```text
Chat API
   ↓
Chat Service
   ↓
Orchestrator
```

Weather:

```text
Weather API
   ↓
Weather Service
   ↓
Weather Agent / Tool
```

---

# 68. Repository Layer

Database access should be separated where practical.

Example:

```text
PFZ Service
   ↓
PFZ Repository
   ↓
PostgreSQL/PostGIS
```

---

# 69. Tool Layer

External systems should be wrapped as tools.

Example:

```text
Weather Tool
Ocean Data Tool
Satellite Data Tool
Geospatial Tool
Routing Tool
Knowledge Search Tool
```

Agents should call tools through defined interfaces.

---

# 70. API-to-Agent Flow

```text
POST /chat
      ↓
Chat Service
      ↓
Orchestrator
      ↓
Planner
      ↓
Agent Registry
      ↓
Selected Agents
      ↓
Tools
      ↓
Results
      ↓
Orchestrator
      ↓
Response
```

---

# 71. API-to-Database Flow

```text
API
 ↓
Service
 ↓
Repository
 ↓
Database
```

The LLM should never directly construct unrestricted SQL against production databases.

---

# 72. SQL Safety

Database operations should use:

```text
Parameterized queries
ORM queries
Validated query builders
```

Do not allow raw user text to become unrestricted SQL.

---

# 73. Geospatial Query Safety

Spatial queries should validate:

```text
Geometry type
Coordinate reference system
Bounding area
Query radius
```

Unbounded spatial queries should be avoided.

---

# 74. API Documentation

FastAPI will automatically provide OpenAPI documentation.

Development endpoints:

```text
/docs
/redoc
```

These should be restricted or disabled appropriately in production.

---

# 75. OpenAPI

The API contract should be generated from:

```text
FastAPI
+
Pydantic
```

This ensures request and response schemas remain synchronized.

---

# 76. Testing

API tests should cover:

```text
Unit tests
Integration tests
Schema tests
Agent tests
Tool tests
Database tests
End-to-end tests
```

---

# 77. API Testing Examples

Test:

```text
Valid coordinate
Invalid coordinate
Missing location
Unknown PFZ
Unavailable weather source
RAG no-result case
Agent failure
Timeout
Authentication failure
Rate limit
```

---

# 78. End-to-End Test

Example:

```text
POST /api/v1/chat

"Is it safe to fish tomorrow morning near Goa?"
```

Expected:

```text
Request accepted
 ↓
Planner
 ↓
Weather
 ↓
Ocean
 ↓
Hazard
 ↓
Geospatial
 ↓
Risk
 ↓
Evidence
 ↓
Final answer
```

---

# 79. API Performance

The API should optimize:

```text
Parallel agent execution
Database connection pooling
Caching
Asynchronous I/O
Batch operations
Result reuse
```

---

# 80. API Reliability

The system should implement:

```text
Timeouts
Retries
Fallbacks
Circuit breaking where appropriate
Graceful degradation
Health checks
```

---

# 81. External API Failure

If an external marine/weather source fails:

```text
External API
     ↓
Failure
     ↓
Retry
     ↓
Fallback if available
     ↓
Return source status
```

The system must not fabricate missing values.

---

# 82. API Response Evidence

Responses should optionally include evidence metadata.

Example:

```json
{
  "response": "Conditions are currently assessed as high risk.",
  "evidence": [
    {
      "type": "weather",
      "source": "...",
      "timestamp": "..."
    },
    {
      "type": "wave",
      "source": "...",
      "timestamp": "..."
    }
  ]
}
```

---

# 83. Visualization Integration

The chat API can return structured visualization objects.

Example:

```json
{
  "response": "...",
  "visualizations": [
    {
      "type": "map",
      "id": "map-001"
    }
  ]
}
```

The frontend renders the visualization.

---

# 84. Language Handling

The API accepts:

```text
language = auto
```

or an explicit language.

Example:

```json
{
  "message": "समुद्र में जाना सुरक्षित है?",
  "language": "auto"
}
```

The language agent determines the response language.

---

# 85. Unit Handling

The API should support normalized internal units.

For example:

```text
Distance → km
Temperature → °C
Wind → standard internal unit
Coordinates → decimal degrees
```

User-facing units can be converted as required.

---

# 86. Final API Flow

```text
                         USER
                           │
                           ▼
                        FRONTEND
                           │
                           ▼
                        FASTAPI
                           │
                    Authentication
                           │
                    Request Validation
                           │
                           ▼
                      CHAT SERVICE
                           │
                           ▼
                     ORCHESTRATOR
                           │
                      ┌────┴────┐
                      ▼         ▼
                   PLANNER     STATE
                      │
                      ▼
                AGENT REGISTRY
                      │
          ┌───────────┼────────────┐
          ▼           ▼            ▼
       WEATHER       OCEAN      GEOSPATIAL
        AGENT        AGENT         AGENT
          │           │            │
          ▼           ▼            ▼
        APIs       Databases     PostGIS
          │           │            │
          └───────────┼────────────┘
                      │
              ┌───────┴────────┐
              ▼                ▼
            RAG             RISK
          QDRANT           ENGINE
              │                │
              └───────┬────────┘
                      ▼
                  SYNTHESIS
                      │
                      ▼
                  VISUALIZATION
                      │
                      ▼
                    RESPONSE
                      │
                      ▼
                   FRONTEND
```

---

# 87. Frozen API Principles

ORCA's API architecture officially follows these principles:

1. FastAPI is the primary backend API framework.
2. APIs are versioned under `/api/v1`.
3. Pydantic defines request and response schemas.
4. Frontend communicates with FastAPI, not databases directly.
5. The Orchestrator controls multi-agent execution.
6. Agents access capabilities through defined tools.
7. Database access is separated from API routes.
8. PostgreSQL handles structured application data.
9. PostGIS handles spatial operations.
10. Qdrant handles semantic knowledge retrieval.
11. MinIO handles object storage.
12. Redis handles caching and temporary state.
13. Long-running operations should support asynchronous execution.
14. Streaming should be supported for complex agentic requests.
15. Every request should have a traceable request ID.
16. Agent tasks should have task IDs.
17. API errors should follow a consistent schema.
18. Input must be validated before processing.
19. Coordinates and time ranges must be validated.
20. External API failures must be handled gracefully.
21. Missing data must never be fabricated.
22. Deterministic calculations must remain outside the LLM.
23. Visualization responses should be structured objects.
24. API documentation should be generated through OpenAPI.
25. Authentication and authorization must protect restricted operations.
26. Production configuration must not expose internal infrastructure unnecessarily.
27. API routes should contain minimal business logic.
28. Services should coordinate application logic.
29. Repositories should manage database access.
30. The architecture must remain modular and testable.
