# ORCA — Deployment Architecture

**Project Name:** ORCA
**Document:** Deployment Architecture
**Document ID:** ORCA-DEP-16
**Version:** 1.0
**Status:** FROZEN BASELINE

---

# 1. Purpose

This document defines how the complete ORCA platform will be:

- Developed
- Run locally
- Containerized
- Connected internally
- Persisted
- Configured
- Tested
- Deployed to production

The local architecture must closely mirror production so that development does not require a major architectural rewrite later.

---

# 2. Deployment Philosophy

ORCA follows:

```text
BUILD ON LAPTOP
      ↓
TEST LOCALLY
      ↓
CONTAINERIZE
      ↓
INTEGRATION TEST
      ↓
DEPLOY
````

The prototype is not treated as a separate throwaway architecture.

The same system should progressively become the final system.

---

# 3. Local Development Architecture

The laptop will run:

```text
Windows
   │
   └── Docker Desktop
          │
          ├── ORCA Frontend
          ├── ORCA Backend
          ├── PostgreSQL + PostGIS
          ├── Redis
          ├── Qdrant
          └── MinIO
```

Existing native PostgreSQL/PostGIS may be retained during early development if required, but the finalized containerized architecture should use controlled service definitions.

---

# 4. Why Docker

Docker provides reproducible environments.

Instead of:

```text
"My laptop has the correct version."
```

ORCA uses:

```text
"ORCA defines the environment."
```

This makes the project easier to:

* Run on another laptop
* Demonstrate
* Test
* Deploy
* Maintain

---

# 5. Docker Desktop

Docker Desktop is the local container management environment.

It provides the Docker runtime required to run ORCA's containerized services.

---

# 6. Windows Requirement

The development environment is:

```text
Windows
+
Docker Desktop
```

ORCA does not require the user to manually install a separate Ubuntu desktop environment.

Docker Desktop handles the underlying virtualization/container infrastructure required by Docker.

---

# 7. Linux Containers

ORCA services will primarily use Linux-based containers.

This does NOT mean the developer needs to use Ubuntu as their everyday operating system.

The host environment remains:

```text
Windows
```

---

# 8. Container Architecture

ORCA will use separate containers for major services.

```text
ORCA Network
│
├── frontend
├── backend
├── postgres
├── redis
├── qdrant
└── minio
```

---

# 9. Frontend Container

Technology:

```text
React
Vite
Node.js
```

Development:

```text
npm run dev
```

Production:

```text
Build React application
        ↓
Static assets
        ↓
Web server
```

---

# 10. Backend Container

Technology:

```text
Python
FastAPI
Uvicorn
```

Responsibilities:

```text
API
Authentication
Orchestration
Agents
Analytics
RAG
External API integration
Database access
```

---

# 11. PostgreSQL Container

PostgreSQL stores structured application data.

Potential data:

```text
Users
Conversations
Messages
Agent tasks
Dataset metadata
Source metadata
System configuration
Audit records
```

---

# 12. PostGIS

PostGIS runs as an extension of PostgreSQL.

It provides:

```text
Geospatial storage
Spatial queries
Distance calculations
Polygon operations
Geofencing
Spatial indexing
```

---

# 13. Redis Container

Redis is used for fast temporary state.

Potential uses:

```text
Caching
Rate limiting
Session-related temporary state
Task state
Short-lived agent coordination
```

Redis is NOT the primary persistent database.

---

# 14. Qdrant Container

Qdrant provides vector search for the RAG system.

It stores:

```text
Embeddings
Document chunks
Vector metadata
```

Qdrant is not the source of truth for structured marine data.

---

# 15. MinIO Container

MinIO provides object storage.

Potential objects:

```text
Uploaded documents
Processed files
Satellite files
Generated reports
Large datasets
Raster files
Intermediate artifacts
```

MinIO is not a relational database.

---

# 16. Storage Separation

ORCA follows:

```text
PostgreSQL
→ Structured application data

PostGIS
→ Spatial data

Qdrant
→ Vector representations

MinIO
→ Files / objects

Redis
→ Temporary high-speed state
```

---

# 17. Persistent Volumes

Stateful services require persistent storage.

```text
PostgreSQL
      ↓
Docker volume

Qdrant
      ↓
Docker volume

MinIO
      ↓
Docker volume

Redis
      ↓
Optional persistence depending on use case
```

---

# 18. Windows Host Storage

The host machine may store Docker data on the D: drive if configured through Docker Desktop.

Conceptually:

```text
C:
Docker Desktop application / system components

D:
Docker virtual disk / container data
```

The exact Docker Desktop storage configuration is an environment setting and should not be hard-coded into ORCA.

---

# 19. Project Source Code

The ORCA source repository should remain separate from Docker's internal storage.

Example:

```text
D:\Projects\ORCA
```

Docker should not be used as the project's source-code folder.

---

# 20. Recommended Local Structure

```text
D:\
└── Projects\
    └── ORCA\
        ├── frontend\
        ├── backend\
        ├── agents\
        ├── analytics\
        ├── ingestion\
        ├── docs\
        ├── infrastructure\
        ├── docker-compose.yml
        ├── .env.example
        └── README.md
```

---

# 21. Infrastructure Directory

Infrastructure configuration should be kept separate.

```text
infrastructure/
├── docker/
├── postgres/
├── qdrant/
├── minio/
└── redis/
```

Only required configuration files should be included.

---

# 22. Docker Compose

The local ORCA stack should be orchestrated using:

```text
Docker Compose
```

Conceptually:

```text
docker compose up
```

starts the required services.

---

# 23. Compose Architecture

```text
docker-compose.yml

services:

  frontend
  backend
  postgres
  redis
  qdrant
  minio
```

The exact image versions should be pinned during implementation.

---

# 24. Internal Network

All ORCA services should communicate through a private Docker network.

```text
orca-network
```

Conceptually:

```text
frontend
   │
backend
   │
├── postgres
├── redis
├── qdrant
└── minio
```

---

# 25. Service Discovery

Inside Docker Compose, services communicate using service names.

Example:

```text
postgres
redis
qdrant
minio
backend
```

The backend should not depend on hardcoded laptop IP addresses.

---

# 26. Backend Configuration

The backend should use environment variables.

Example:

```text
DATABASE_URL
REDIS_URL
QDRANT_URL
MINIO_ENDPOINT
LLM_API_KEY
WEATHER_API_KEY
```

---

# 27. Environment Files

Repository:

```text
.env.example
```

Local machine:

```text
.env
```

The real `.env` must never be committed.

---

# 28. Example Configuration

```text
DATABASE_URL=...
REDIS_URL=...
QDRANT_URL=...
MINIO_ENDPOINT=...
LLM_API_KEY=...
```

Actual credentials are environment-specific.

---

# 29. Development vs Production

ORCA has two deployment configurations:

```text
Development
Production
```

They use the same application architecture but different:

```text
Credentials
Domains
Scaling
Logging
Security settings
Resource allocation
```

---

# 30. Development Environment

Development prioritizes:

```text
Fast iteration
Debugging
Local access
Hot reload
Developer logs
```

---

# 31. Production Environment

Production prioritizes:

```text
Security
Reliability
Availability
Performance
Monitoring
Backups
Scalability
```

---

# 32. Frontend → Backend

Local:

```text
Browser
 ↓
localhost
 ↓
Frontend
 ↓
Backend API
```

Production:

```text
User
 ↓
HTTPS
 ↓
Frontend
 ↓
Backend API
```

---

# 33. Backend → Database

```text
Backend
   │
   ├── PostgreSQL
   └── PostGIS
```

The browser must never connect directly to PostgreSQL.

---

# 34. Backend → Qdrant

```text
Backend
   ↓
RAG service
   ↓
Qdrant
```

The frontend must not directly query Qdrant.

---

# 35. Backend → MinIO

```text
Backend
   ↓
Object storage service
   ↓
MinIO
```

The backend controls access to stored objects.

---

# 36. Backend → Redis

```text
Backend
   ↓
Redis
```

Redis remains an internal infrastructure component.

---

# 37. External APIs

External APIs are accessed through backend services.

```text
ORCA Backend
     ↓
External API
```

Examples may include:

```text
Weather services
Marine services
Satellite services
Mapping services
LLM providers
```

---

# 38. External API Failure

ORCA must not crash because one external service becomes unavailable.

Instead:

```text
External API unavailable
        ↓
Service reports failure
        ↓
Agent receives failure state
        ↓
Orchestrator replans
        ↓
Partial result / alternative source
```

---

# 39. Health Checks

Each service should expose or support health verification.

Example:

```text
Backend → /health
```

Infrastructure health:

```text
PostgreSQL → healthy
Redis → healthy
Qdrant → healthy
MinIO → healthy
```

---

# 40. Startup Dependency

The backend should not assume that databases are instantly ready when Docker starts.

Startup should account for:

```text
Container started
≠
Service ready
```

Health checks and retry logic should be used.

---

# 41. Backend Startup

Conceptually:

```text
Docker starts
     ↓
PostgreSQL starts
     ↓
PostGIS ready
     ↓
Qdrant ready
     ↓
MinIO ready
     ↓
Redis ready
     ↓
Backend starts
```

---

# 42. Database Initialization

Initial database setup may include:

```text
Schema creation
PostGIS extension
Indexes
Initial configuration
Required seed data
```

Migrations should be used rather than manually recreating production schemas.

---

# 43. Database Migrations

Recommended:

```text
Alembic
```

Migration flow:

```text
Code change
 ↓
Migration
 ↓
Database schema update
```

---

# 44. RAG Initialization

The RAG system should have a controlled ingestion pipeline.

```text
Documents
 ↓
Validation
 ↓
Text extraction
 ↓
Chunking
 ↓
Embedding
 ↓
Qdrant
```

It should not automatically ingest arbitrary files placed into a folder.

---

# 45. MinIO Initialization

Buckets should be created explicitly.

Potential buckets:

```text
documents
datasets
rasters
reports
artifacts
```

Actual bucket names can be finalized during implementation.

---

# 46. Qdrant Collections

Collections should be created deliberately.

Example:

```text
marine_knowledge
```

Metadata should support filtering.

---

# 47. Redis Usage

Redis should contain only data that the application can safely recreate when appropriate.

Persistent critical business data belongs in PostgreSQL.

---

# 48. Docker Volumes

Named volumes are preferred for persistent infrastructure data.

Example conceptually:

```text
postgres_data
qdrant_data
minio_data
redis_data
```

---

# 49. Volume Backup

Persistent data must be backed up separately from containers.

Containers are disposable.

Data is not.

---

# 50. Container Lifecycle

ORCA should follow:

```text
Container
    ↓
Disposable

Volume
    ↓
Persistent
```

Deleting a container should not automatically destroy production data.

---

# 51. Logging

Each service should write structured logs.

Example:

```text
timestamp
service
request_id
task_id
level
message
```

---

# 52. Observability

Production monitoring should eventually include:

```text
Application logs
Metrics
Health checks
Error tracking
Request tracing
```

---

# 53. Resource Management

Each container should have reasonable CPU and memory limits in production.

Avoid allowing one service to consume the entire machine.

---

# 54. Local Laptop Resources

The laptop does not need to run every advanced ML workload locally.

The architecture should distinguish:

```text
Application services
```

from:

```text
Heavy model training
```

---

# 55. LLM Deployment

ORCA does not require a local LLM.

The LLM layer can use external APIs.

```text
ORCA Agent
    ↓
LLM API
    ↓
Model Provider
```

This avoids downloading large language models to the laptop.

---

# 56. GPU Requirement

The base ORCA architecture should not require a dedicated GPU.

CPU execution should be sufficient for:

```text
FastAPI
PostgreSQL/PostGIS
Redis
Qdrant
MinIO
Classical analytics
Basic ML
```

---

# 57. Heavy ML

If advanced models are introduced later, they can run:

```text
Cloud GPU
Dedicated server
External inference API
```

without redesigning ORCA.

---

# 58. Development Workflow

Recommended:

```text
Write code
 ↓
Run services
 ↓
Test API
 ↓
Test agents
 ↓
Test analytics
 ↓
Test RAG
 ↓
Test frontend
 ↓
Integration test
```

---

# 59. Local Development Modes

During early development, individual services may run natively when useful.

Example:

```text
Frontend → npm run dev
Backend → uvicorn
PostgreSQL → local installation
```

Docker becomes the standardized integrated environment.

---

# 60. Final Local Mode

The final local ORCA environment should preferably be:

```text
Docker Compose
    ↓
Complete ORCA stack
```

This ensures the system can be started consistently.

---

# 61. Production Architecture

A production deployment may look like:

```text
                         INTERNET
                            │
                            ▼
                     Reverse Proxy
                            │
                         HTTPS
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
        Frontend                       Backend
                                            │
                 ┌──────────────────────────┼───────────────┐
                 ▼                          ▼               ▼
             PostgreSQL                  Redis           Qdrant
                 │
              PostGIS
                 │
                 └───────────────┐
                                 ▼
                               MinIO
```

---

# 62. Reverse Proxy

Production should use a reverse proxy / ingress layer for:

```text
HTTPS
Routing
Headers
Compression
Security policies
```

Possible technologies:

```text
Nginx
Traefik
Cloud load balancer
```

The final choice is deployment-specific.

---

# 63. Domain Structure

Potential production structure:

```text
orca.example.com
api.orca.example.com
```

The actual domain is deployment-specific.

---

# 64. TLS

Production must use valid TLS certificates.

```text
HTTPS
```

must be enforced for public traffic.

---

# 65. Database Production Architecture

For production:

```text
Application
     ↓
Managed / secured PostgreSQL
     +
PostGIS
```

A managed PostgreSQL provider may be preferable to manually maintaining the database.

---

# 66. Production Qdrant

Possible deployment:

```text
Managed Qdrant
```

or:

```text
Self-hosted Qdrant
```

depending on scale and budget.

---

# 67. Production Object Storage

Possible deployment:

```text
MinIO
```

or a compatible cloud object-storage service.

The application should interact through an object-storage abstraction so that infrastructure can change later.

---

# 68. Production Redis

Possible:

```text
Managed Redis
```

or:

```text
Self-hosted Redis
```

depending on deployment requirements.

---

# 69. Horizontal Scaling

The backend should ideally be stateless enough that multiple backend instances can run:

```text
                Load Balancer
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Backend    Backend    Backend
```

Shared state belongs in:

```text
PostgreSQL
Redis
Qdrant
MinIO
```

rather than local container files.

---

# 70. Agent Scaling

Agents should execute as logical application components initially.

If workloads become large, agent execution can later move to workers.

```text
API
 ↓
Task Queue
 ↓
Worker
 ↓
Agent
```

---

# 71. Background Jobs

Suitable background jobs:

```text
Dataset ingestion
Embedding generation
Large raster processing
Report generation
Scheduled data synchronization
Cache refresh
```

These should not unnecessarily block HTTP requests.

---

# 72. Worker Architecture

Future scalable architecture:

```text
FastAPI
   ↓
Redis / Task Queue
   ↓
Worker
   ↓
Analytics / RAG / Ingestion
```

---

# 73. Scheduled Data Pipelines

External datasets may require scheduled ingestion.

Example:

```text
Scheduler
   ↓
Fetch dataset
   ↓
Validate
   ↓
Transform
   ↓
PostGIS / MinIO
   ↓
Update metadata
```

---

# 74. Deployment Environments

Recommended environments:

```text
Development
Testing
Production
```

At minimum:

```text
Development
Production
```

must be separated.

---

# 75. Testing Environment

The testing environment should use isolated:

```text
Database
Object storage
Vector database
Redis
```

so testing cannot corrupt production data.

---

# 76. CI/CD

Future pipeline:

```text
Git Push
   ↓
CI
   ↓
Lint
   ↓
Unit Tests
   ↓
Integration Tests
   ↓
Security Checks
   ↓
Build Docker Images
   ↓
Deploy
```

---

# 77. Container Registry

Production images should be stored in a container registry.

Potential options:

```text
GitHub Container Registry
Docker Hub
Cloud provider registry
```

The exact provider is deployment-specific.

---

# 78. Image Versioning

Avoid relying only on:

```text
latest
```

Prefer versioned images:

```text
orca-backend:1.0.0
orca-backend:1.1.0
```

---

# 79. Rollback

Deployment should allow:

```text
Version 2
 ↓
Problem
 ↓
Rollback
 ↓
Version 1
```

---

# 80. Database Migration Safety

Application deployment and database migrations must be coordinated.

Never assume that an arbitrary old database is immediately compatible with a new application version.

---

# 81. Backup Strategy

Production should back up:

```text
PostgreSQL
PostGIS
Qdrant
MinIO
Configuration
```

with appropriate retention.

---

# 82. Disaster Recovery

Recovery plan should address:

```text
Database loss
Storage loss
Container failure
Server failure
External API outage
Credential compromise
```

---

# 83. Secrets

Production secrets should be stored using:

```text
Cloud secret manager
Deployment secret store
Environment secrets
```

rather than committed configuration files.

---

# 84. No Secrets in Images

Docker images must never contain:

```text
.env
API keys
passwords
private certificates
database credentials
```

---

# 85. Security Boundary

Public:

```text
Frontend
API / Reverse Proxy
```

Private:

```text
PostgreSQL
PostGIS
Redis
Qdrant
MinIO
Internal workers
```

---

# 86. Firewall

Only required public ports should be exposed.

Internal service ports should remain private.

---

# 87. Production Port Concept

Public:

```text
443
```

Internal services:

```text
PostgreSQL → 5432
Redis → 6379
Qdrant → internal
MinIO → internal / controlled
```

The actual network configuration depends on the deployment environment.

---

# 88. Local Ports

Development may expose services for debugging.

For example:

```text
Frontend
Backend
PostgreSQL
Qdrant
MinIO
```

But production should not expose unnecessary administrative interfaces.

---

# 89. Admin Interfaces

Administrative interfaces should require authentication and should not be publicly exposed by default.

---

# 90. Production Data Flow

```text
User
 ↓
HTTPS
 ↓
Reverse Proxy
 ↓
Frontend
 ↓
FastAPI
 ↓
Orchestrator
 ↓
Agents
 ↓
Tools / Analytics / RAG
 ↓
┌─────────────┬─────────────┬─────────────┐
PostGIS      Qdrant        MinIO        APIs
 ↓             ↓             ↓             ↓
Structured   Knowledge     Files         External
Data         Retrieval     Storage       Sources
```

---

# 91. Failure Isolation

Failure of:

```text
Redis
```

should not destroy:

```text
PostgreSQL
```

Failure of:

```text
Qdrant
```

should not destroy:

```text
PostGIS
```

Services should remain independently recoverable.

---

# 92. Graceful Degradation

Example:

```text
Qdrant unavailable
       ↓
RAG unavailable
       ↓
ORCA reports knowledge retrieval unavailable
       ↓
Other analytical capabilities continue
```

The system must not invent missing evidence.

---

# 93. Disaster Recovery Priority

Priority:

```text
1. PostgreSQL / PostGIS
2. MinIO
3. Qdrant
4. Configuration
5. Redis
```

Redis is generally more reconstructable than primary application data.

---

# 94. Local Development Storage

Recommended organization:

```text
C:
Docker Desktop/system components

D:
ORCA source code
Docker data/disk image
Project datasets
Persistent development data
```

This keeps large project-related storage away from the C: drive where practical.

---

# 95. Important Docker Principle

Docker Desktop itself and Docker's internal data storage are separate concepts.

```text
Docker Desktop
→ Application/runtime management

Docker data
→ Images
→ Containers
→ Volumes
→ Build cache
```

The data location can be configured separately.

---

# 96. ORCA Storage Classification

```text
Source Code
→ Git repository

Structured Data
→ PostgreSQL/PostGIS

Vector Data
→ Qdrant

Files
→ MinIO

Temporary Cache
→ Redis

Docker Infrastructure
→ Docker storage
```

---

# 97. Reproducibility

A fresh machine should eventually be able to run:

```text
git clone
      ↓
configure environment
      ↓
docker compose up
      ↓
ORCA starts
```

without manually recreating every infrastructure component.

---

# 98. Development Completion Criteria

Deployment architecture is considered implemented when:

```text
Docker starts successfully
        ↓
All services become healthy
        ↓
Backend connects to PostgreSQL/PostGIS
        ↓
Backend connects to Redis
        ↓
Backend connects to Qdrant
        ↓
Backend connects to MinIO
        ↓
Frontend connects to backend
        ↓
Agents execute
        ↓
RAG works
        ↓
Analytics work
        ↓
End-to-end query works
```

---

# 99. Production Completion Criteria

Production deployment is considered ready when:

```text
HTTPS works
Authentication works
Authorization works
Backups work
Monitoring works
Logging works
Secrets are protected
Database is secured
Internal services are private
Health checks work
Rollback is possible
External API failures are handled
```

---

# 100. Frozen Deployment Architecture

ORCA officially follows these deployment principles:

1. Docker is the standardized local integrated environment.
2. Docker Desktop runs on the Windows development machine.
3. ORCA does not require Ubuntu as the host operating system.
4. ORCA services use Linux containers where appropriate.
5. Frontend and backend are separate services.
6. PostgreSQL is the primary relational database.
7. PostGIS provides spatial database capabilities.
8. Redis provides temporary/cache/coordination capabilities.
9. Qdrant provides vector search.
10. MinIO provides object storage.
11. Stateful services use persistent volumes.
12. Source code remains separate from Docker's internal storage.
13. Environment variables provide configuration.
14. Secrets are never committed to Git.
15. Services communicate through private networks.
16. Databases are not directly accessed by the frontend.
17. Qdrant is not directly accessed by the frontend.
18. MinIO access is controlled by the backend.
19. External APIs are accessed through backend services.
20. Database migrations use a controlled migration system.
21. Health checks are required for integrated deployment.
22. Services must tolerate startup ordering.
23. External service failures must be handled gracefully.
24. Background processing should use workers when workloads require it.
25. Heavy ML workloads are not required to run locally.
26. The base architecture does not require a dedicated GPU.
27. Production uses HTTPS.
28. Production internal services remain private.
29. Production secrets use secure secret storage.
30. Production data is backed up.
31. Container images are versioned.
32. Deployment must support rollback.
33. Development and production environments remain isolated.
34. The local architecture should closely mirror production.
35. ORCA should ultimately be reproducible through its infrastructure configuration.
