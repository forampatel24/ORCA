# ORCA — Development Environment

**Project Name:** ORCA  
**Document:** Development Environment & Local Setup  
**Document ID:** ORCA-DEV-19  
**Version:** 1.0  
**Status:** FROZEN BASELINE

---

# 1. Purpose

This document defines the complete local development environment for ORCA.

The goal is to ensure that the entire ORCA platform can be developed and executed consistently on the development laptop without changing the architecture later.

The local environment will use:

- Windows
- Docker Desktop
- PostgreSQL
- PostGIS
- Redis
- Qdrant
- MinIO
- Python
- Node.js
- Git
- VS Code
- Browser-based frontend

---

# 2. Development Philosophy

The development environment should mirror the intended production architecture as closely as reasonably possible.

We do NOT want:

```text
Prototype architecture
        ↓
Throw it away
        ↓
Production architecture
````

Instead:

```text
Final Architecture
       ↓
Local Implementation
       ↓
Prototype
       ↓
Testing
       ↓
Production
```

The prototype should therefore be a working subset of the final ORCA system.

---

# 3. Operating System

Primary development OS:

```text
Windows 11
```

The project will run using:

```text
Windows
+
Docker Desktop
```

Linux/Ubuntu is NOT required as the primary development environment.

---

# 4. Docker Desktop

Docker Desktop is the local container-management environment.

It will be used to run infrastructure services that should remain isolated from the Windows host.

Primary containerized services:

```text
Redis
Qdrant
MinIO
Prometheus
Grafana
Jaeger
```

Other services may also be containerized later where useful.

---

# 5. Docker Storage

Docker Desktop itself may remain installed on the Windows system drive.

Docker's large data/disk-image storage should be configured on:

```text
D:\
```

This prevents Docker's growing container/image/volume storage from unnecessarily consuming C: drive space.

---

# 6. Project Location

The ORCA source code should be stored on:

```text
D:\
```

Recommended:

```text
D:\Projects\ORCA\
```

Example:

```text
D:\Projects\ORCA
│
├── backend
├── frontend
├── agents
├── data
├── infrastructure
├── scripts
├── tests
├── docs
└── .env
```

---

# 7. PostgreSQL

PostgreSQL is the primary relational database.

It will store structured application information.

Examples:

```text
Users
Conversations
Tasks
Agent executions
Dataset metadata
Marine observations
Weather observations
Risk results
Geofences
Routes
Alerts
Audit information
```

---

# 8. PostGIS

PostGIS extends PostgreSQL with geospatial capabilities.

ORCA will use PostGIS for:

```text
Point queries
Polygon queries
Distance calculations
Spatial intersections
Geofencing
Marine boundaries
Fishing regions
Restricted areas
Coastal regions
Route-related spatial operations
```

PostGIS is therefore a core component of ORCA.

---

# 9. PostgreSQL + PostGIS Relationship

PostGIS is NOT a separate database.

The architecture is:

```text
PostgreSQL
     |
     └── PostGIS Extension
```

Therefore:

```text
PostgreSQL = Database
PostGIS    = Geospatial extension
```

---

# 10. Redis

Redis is used as the fast in-memory data layer.

Primary uses:

```text
Caching
Temporary task state
Session-related state where appropriate
Rate limiting
Short-lived results
Agent workflow state where appropriate
```

Redis is NOT the primary permanent database.

---

# 11. Qdrant

Qdrant is the vector database.

It will be used for ORCA's RAG system.

Possible stored information:

```text
Marine advisories
Government documents
Operational guidelines
Dataset documentation
Marine safety information
Knowledge-base chunks
Historical textual information
```

The exact ingestion sources will be defined by the data/RAG architecture.

---

# 12. MinIO

MinIO provides S3-compatible object storage.

It will store large files and objects that should not be placed directly inside PostgreSQL.

Examples:

```text
Satellite files
Raster files
Uploaded datasets
Raw API responses
Processed data files
Documents
Generated reports
Large geospatial files
```

Architecture:

```text
Application
     |
     ├── Structured data → PostgreSQL/PostGIS
     |
     ├── Vector data → Qdrant
     |
     └── Large files → MinIO
```

---

# 13. Why We Need Multiple Storage Systems

ORCA has different types of data.

Therefore:

```text
                    ORCA DATA
                       |
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
 Structured         Vectors           Files
       |               |                |
 PostgreSQL          Qdrant            MinIO
 + PostGIS
```

Redis provides a fourth layer:

```text
Fast temporary/cache data
```

---

# 14. Database Responsibilities

| Component  | Responsibility                          |
| ---------- | --------------------------------------- |
| PostgreSQL | Structured persistent data              |
| PostGIS    | Geospatial operations inside PostgreSQL |
| Redis      | Cache and temporary fast state          |
| Qdrant     | Vector search / RAG                     |
| MinIO      | Large object/file storage               |

---

# 15. Python

Python is the primary backend/AI language.

It will be used for:

```text
FastAPI
AI agents
LLM integration
RAG
Data processing
Geospatial processing
Analytics
ETL pipelines
Machine learning components
Risk calculations
API integrations
```

---

# 16. Python Environment

The backend should use a virtual environment during local development.

Recommended:

```text
.venv
```

Example:

```text
D:\Projects\ORCA\backend\.venv
```

Dependencies should be managed through:

```text
requirements.txt
```

or a modern Python dependency manager if adopted later.

---

# 17. Backend Framework

Backend:

```text
FastAPI
```

FastAPI will expose:

```text
REST APIs
Agent endpoints
RAG endpoints
Data endpoints
Geospatial endpoints
Routing endpoints
Alert endpoints
Health endpoints
```

---

# 18. Node.js

Node.js will be used for the frontend development environment.

The frontend will use:

```text
Node.js
npm
```

---

# 19. Frontend

Frontend stack:

```text
React
TypeScript
Vite
```

UI technologies:

```text
Tailwind CSS
```

or the final selected UI framework/design system.

---

# 20. Frontend Responsibilities

The frontend will provide:

```text
Chat interface
Interactive maps
Marine condition visualization
Risk visualization
Alerts
Routes
Charts
Agent activity/status where appropriate
Evidence
Recommendations
```

---

# 21. Maps

The frontend will require a geospatial mapping library.

Recommended architecture:

```text
React
   |
   └── Map library
          |
          └── Geospatial layers
```

Possible implementation:

```text
MapLibre GL JS
```

with appropriate map tile/data sources.

The final map provider can be selected during implementation without changing the core architecture.

---

# 22. Geospatial Backend

Python geospatial tooling may include:

```text
GeoPandas
Shapely
PyProj
Rasterio
```

depending on the exact dataset formats and processing requirements.

---

# 23. Database Drivers

Python will communicate with PostgreSQL/PostGIS through a PostgreSQL driver and ORM/database layer.

Recommended:

```text
SQLAlchemy
psycopg
```

The exact ORM usage should remain consistent across the backend.

---

# 24. Redis Client

Python services will communicate with Redis using an appropriate Redis Python client.

Redis should remain behind an application abstraction where practical.

---

# 25. Qdrant Client

The backend will communicate with Qdrant through the official Python client.

The application should not directly depend on low-level Qdrant implementation details throughout the codebase.

Use a dedicated vector-store/retrieval layer.

---

# 26. MinIO Client

MinIO will be accessed through its S3-compatible API.

The application should use a storage abstraction where practical:

```text
StorageService
     |
     └── MinIO/S3
```

---

# 27. LLM Provider

ORCA will use an external LLM API.

The API key will be stored in:

```text
.env
```

Example:

```text
LLM_API_KEY=...
```

The actual key must NEVER be committed to Git.

---

# 28. Agent Architecture

Agents will run as backend services/modules.

Conceptually:

```text
FastAPI
   |
   ↓
Agent Orchestrator
   |
   ├── Planner
   ├── Marine Data Agent
   ├── Weather Agent
   ├── Ocean Agent
   ├── Geospatial Agent
   ├── Risk Agent
   ├── Routing Agent
   ├── RAG Agent
   ├── Visualization Agent
   └── Reporting Agent
```

The exact agent list is defined in the agent architecture document.

---

# 29. Agent Communication

Agents should communicate through controlled interfaces rather than directly modifying each other's internal state.

Preferred pattern:

```text
Agent
 ↓
Tool / Service
 ↓
Structured Result
 ↓
Orchestrator
 ↓
Next Agent
```

---

# 30. External APIs

ORCA will communicate with external services for:

```text
Weather
Marine observations
Satellite/Earth Observation
Marine advisories
Mapping
Routing
Other authoritative data sources
```

External API credentials belong in environment variables.

---

# 31. Environment Variables

A local:

```text
.env
```

file will contain configuration such as:

```text
DATABASE_URL
REDIS_URL
QDRANT_URL
MINIO_ENDPOINT
MINIO_ACCESS_KEY
MINIO_SECRET_KEY
LLM_API_KEY
EXTERNAL_API_KEYS
```

Actual values must never be committed.

---

# 32. Environment Template

The repository should contain:

```text
.env.example
```

Example:

```text
DATABASE_URL=
REDIS_URL=
QDRANT_URL=
MINIO_ENDPOINT=
MINIO_ACCESS_KEY=
MINIO_SECRET_KEY=
LLM_API_KEY=
```

No real credentials should appear in `.env.example`.

---

# 33. Git

Git will be used for source control.

Recommended repository structure:

```text
ORCA
 |
 ├── main
 ├── develop
 └── feature/*
```

The exact branching strategy can be adapted for the team.

---

# 34. GitHub

GitHub will host the source repository.

The repository should contain:

```text
Source code
Documentation
Configuration templates
Tests
Docker configuration
Database migrations
```

It should NOT contain:

```text
API keys
Passwords
Private datasets
Large generated files
Secrets
```

---

# 35. VS Code

Recommended primary IDE:

```text
Visual Studio Code
```

Useful extensions:

```text
Python
Pylance
ESLint
Prettier
Docker
GitLens
REST Client
```

Exact extensions are optional.

---

# 36. Terminal

Windows development can use:

```text
PowerShell
```

for normal project commands.

Docker commands will be executed through:

```text
PowerShell
```

or VS Code's integrated terminal.

---

# 37. Docker Compose

Docker Compose will define the local infrastructure.

Conceptually:

```text
docker-compose.yml
```

will define services such as:

```text
redis
qdrant
minio
prometheus
grafana
jaeger
```

The exact configuration will be created during infrastructure implementation.

---

# 38. Local Architecture

Final local environment:

```text
                       WINDOWS
                          |
                    Docker Desktop
                          |
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
      Redis             Qdrant            MinIO
        |                 |                 |
        └─────────────────┼─────────────────┘
                          |
                     ORCA Backend
                          |
                 PostgreSQL + PostGIS
                          |
                    External APIs
```

Monitoring:

```text
ORCA
 |
 ├── Prometheus
 ├── Grafana
 └── Jaeger
```

---

# 39. PostgreSQL Deployment

PostgreSQL/PostGIS may remain installed directly on Windows because it is already available.

The project does not require duplicating PostgreSQL unnecessarily inside Docker if the existing installation is configured correctly.

Therefore:

```text
Windows
 └── PostgreSQL + PostGIS

Docker
 ├── Redis
 ├── Qdrant
 ├── MinIO
 ├── Prometheus
 ├── Grafana
 └── Jaeger
```

This is the preferred current local arrangement.

---

# 40. Docker Network

Docker services should communicate using a dedicated Compose network.

Conceptually:

```text
orca-network
```

Services:

```text
redis
qdrant
minio
prometheus
grafana
jaeger
```

---

# 41. Ports

Development ports should be explicitly documented.

Example conceptual configuration:

```text
FastAPI       → 8000
React/Vite    → 5173
PostgreSQL    → 5432
Redis         → 6379
Qdrant        → 6333
MinIO         → 9000
Grafana       → 3000
Prometheus    → 9090
Jaeger        → 16686
```

Ports may be changed if conflicts exist.

---

# 42. Port Conflicts

Before starting the complete stack:

```text
Check ports
 ↓
Identify conflicts
 ↓
Change only conflicting development port
 ↓
Update environment configuration
```

Do not randomly change ports across different configuration files.

---

# 43. Database Naming

A dedicated ORCA PostgreSQL database should be created.

Example:

```text
orca_db
```

The database should contain ORCA schemas/tables rather than mixing project data with unrelated databases.

---

# 44. PostgreSQL Schemas

Logical separation may be used for areas such as:

```text
application
marine
geospatial
analytics
audit
```

The exact schema design will be finalized in the database architecture document.

---

# 45. Database Migrations

Database structure must be version-controlled.

Recommended:

```text
Alembic
```

for PostgreSQL/SQLAlchemy migrations.

Do not manually modify production-like schemas without migrations.

---

# 46. Seed Data

Development may use controlled seed data.

Examples:

```text
Sample users
Sample geofences
Sample marine observations
Sample advisories
Sample documents
```

Seed data must be clearly separated from real production data.

---

# 47. Dataset Storage

Datasets should be organized separately from source code.

Recommended:

```text
D:\Projects\ORCA\data\
```

with:

```text
data
├── raw
├── processed
├── external
├── sample
└── temporary
```

---

# 48. Raw Data

Raw external datasets should be stored under:

```text
data/raw/
```

They should not be modified after ingestion.

---

# 49. Processed Data

Processed datasets belong under:

```text
data/processed/
```

Processing pipelines should be reproducible.

---

# 50. Large Data

Very large datasets should eventually be stored in:

```text
MinIO
```

rather than committed to Git.

Local filesystem storage can be used during controlled development when appropriate.

---

# 51. Database Backups

Development databases should have a backup strategy before destructive schema operations.

Example:

```text
PostgreSQL dump
```

The backup location should preferably be on:

```text
D:\
```

rather than consuming C: drive space.

---

# 52. Startup Order

The local system should start approximately as:

```text
1. Docker Desktop
2. Infrastructure containers
3. PostgreSQL
4. Backend
5. Frontend
```

The backend should verify required dependencies before accepting requests.

---

# 53. Shutdown

Normal shutdown:

```text
Frontend
 ↓
Backend
 ↓
Docker services
```

Docker volumes should NOT be deleted during normal shutdown.

---

# 54. Persistence

Persistent Docker volumes should be used for:

```text
Redis where required
Qdrant
MinIO
Monitoring systems
```

so container recreation does not automatically destroy application data.

---

# 55. Docker Volumes

Never confuse:

```text
Container
```

with:

```text
Persistent volume
```

Containers can be recreated.

Persistent volumes preserve data.

---

# 56. C: Drive vs D: Drive

Recommended division:

```text
C:
Windows
Docker Desktop application/system components
Normal Windows applications

D:
ORCA source code
ORCA datasets
Docker data/disk image
Large Docker volumes
PostgreSQL project backups
Generated large files
```

---

# 57. Storage Strategy

The objective is:

```text
C: = Operating system + applications
D: = Project + large development data
```

This reduces unnecessary pressure on the system drive.

---

# 58. No Unnecessary Services

Do not install infrastructure simply because it exists.

Each component must have a clear purpose:

```text
PostgreSQL/PostGIS → structured + geospatial data
Redis             → cache/temporary state
Qdrant            → vector/RAG
MinIO             → object storage
Prometheus        → metrics
Grafana           → dashboards
Jaeger            → tracing
```

---

# 59. Local Security

Never expose development services publicly unless explicitly required.

Prefer:

```text
localhost
```

for local infrastructure.

---

# 60. Credentials

Generate separate development credentials.

Do not reuse:

```text
Production passwords
Production API keys
Production secrets
```

---

# 61. CORS

The backend should explicitly allow the local frontend origin.

Example:

```text
http://localhost:5173
```

Do not use unrestricted CORS in production.

---

# 62. Development Workflow

Normal development:

```text
1. Pull latest code
2. Start Docker Desktop
3. Start infrastructure
4. Activate Python environment
5. Start FastAPI
6. Start React
7. Develop
8. Run tests
9. Inspect logs/metrics
10. Commit changes
```

---

# 63. Backend Command Concept

Development backend:

```text
uvicorn
```

with reload enabled during development.

Production deployment should use an appropriate production server configuration.

---

# 64. Frontend Development

Frontend:

```text
npm install
npm run dev
```

The exact scripts will be defined in `package.json`.

---

# 65. Testing Environment

Testing should not depend entirely on production data.

Use:

```text
Unit tests
Integration tests
API tests
Agent tests
RAG tests
Geospatial tests
End-to-end tests
```

---

# 66. Test Database

Automated tests should ideally use an isolated database/environment.

Do not allow tests to accidentally modify important development data.

---

# 67. Health Verification

After starting ORCA:

```text
Backend health
Database connectivity
Redis connectivity
Qdrant connectivity
MinIO connectivity
LLM availability
External API availability
```

should be verified.

---

# 68. First Local Milestone

Before implementing the complete agentic system, the environment should achieve:

```text
Windows
   +
Docker
   +
PostgreSQL/PostGIS
   +
Redis
   +
Qdrant
   +
MinIO
   +
FastAPI
   +
React
```

all communicating successfully.

---

# 69. Second Local Milestone

Then add:

```text
LLM API
   +
RAG
   +
Agent Orchestrator
```

---

# 70. Third Local Milestone

Then add:

```text
Marine data
Weather
Ocean analytics
Geospatial reasoning
Risk analysis
Routing
```

---

# 71. Fourth Local Milestone

Then add:

```text
Alerts
Maps
Visualization
Evidence
Explainability
Monitoring
```

---

# 72. Development Environment Acceptance Criteria

The environment is considered correctly configured when:

1. ORCA backend starts successfully.
2. Frontend starts successfully.
3. PostgreSQL is reachable.
4. PostGIS queries work.
5. Redis is reachable.
6. Qdrant is reachable.
7. MinIO is reachable.
8. LLM API can be accessed securely.
9. Docker services persist data correctly.
10. Environment variables are loaded correctly.
11. No secrets are committed.
12. Logs are generated.
13. Health checks work.
14. Database migrations work.
15. The complete environment can be recreated from documented configuration.

---

# 73. Frozen Local Stack

The current ORCA development stack is:

```text
OPERATING SYSTEM
Windows 11

CONTAINER PLATFORM
Docker Desktop

BACKEND
Python
FastAPI

FRONTEND
React
TypeScript
Vite

DATABASE
PostgreSQL
PostGIS

CACHE
Redis

VECTOR DATABASE
Qdrant

OBJECT STORAGE
MinIO

GEOSPATIAL
GeoPandas
Shapely
PyProj
Rasterio

ORM / DATABASE
SQLAlchemy
psycopg
Alembic

AI
External LLM API
RAG
Multi-Agent Architecture

MAPS
MapLibre GL JS / equivalent

OBSERVABILITY
OpenTelemetry
Prometheus
Grafana
Jaeger

VERSION CONTROL
Git
GitHub

IDE
VS Code
```

---

# 74. Final Architecture Principle

ORCA will not be built as:

```text
"Prototype first, architecture later."
```

It will be built as:

```text
FINAL ARCHITECTURE
       ↓
LOCAL IMPLEMENTATION
       ↓
INCREMENTAL DEVELOPMENT
       ↓
PROTOTYPE CHECKPOINT
       ↓
COMPLETE SYSTEM
```

The prototype is therefore a checkpoint in the development process, not a separate simplified architecture.

---

# 75. Status

This document freezes the ORCA local development environment.

Future implementation may change:

* Exact package versions
* Exact Docker image versions
* Port numbers if conflicts occur
* Specific external APIs
* Map provider
* Monitoring configuration

but the core local architecture remains:

```text
Windows
+
Docker Desktop
+
PostgreSQL/PostGIS
+
Redis
+
Qdrant
+
MinIO
+
FastAPI
+
React/TypeScript
+
LLM API
+
RAG
+
Multi-Agent Architecture
+
Geospatial Processing
+
Observability
```

