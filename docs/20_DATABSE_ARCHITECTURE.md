# ORCA — Database Architecture

**Project Name:** ORCA  
**Document:** Database Architecture  
**Document ID:** ORCA-DB-20  
**Version:** 1.0  
**Status:** FROZEN BASELINE

---

# 1. Purpose

This document defines the complete data-storage architecture of ORCA.

ORCA uses multiple storage technologies because its data is heterogeneous:

- relational data
- geospatial data
- vector embeddings
- temporary/cache data
- large files and Earth Observation datasets

The system therefore follows a polyglot-storage architecture.

---

# 2. Storage Architecture

ORCA uses four primary storage systems:

```text
                    ORCA DATA
                       |
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
 Structured         Vector            Objects
       |               |                |
 PostgreSQL         Qdrant            MinIO
 + PostGIS
       |
       └──── Redis → cache / temporary state
````

---

# 3. Database Responsibilities

| Technology | Primary Role                             |
| ---------- | ---------------------------------------- |
| PostgreSQL | Persistent structured application data   |
| PostGIS    | Geospatial data and spatial queries      |
| Redis      | Cache, temporary state, fast-access data |
| Qdrant     | Vector database for RAG                  |
| MinIO      | Object/file storage                      |

---

# 4. PostgreSQL

PostgreSQL is ORCA's primary persistent relational database.

It stores information that requires:

* relationships
* transactions
* constraints
* indexing
* structured querying
* reliable persistence

Examples:

```text
Users
Conversations
Messages
Tasks
Agent executions
Dataset metadata
Marine observations
Weather observations
Risk assessments
Routes
Alerts
Geofences
Audit records
```

---

# 5. PostGIS

PostGIS is installed as an extension to PostgreSQL.

It provides spatial capabilities such as:

```text
Point
LineString
Polygon
MultiPolygon
Distance
Intersection
Containment
Buffer
Spatial joins
Coordinate transformations
```

PostGIS is therefore used whenever ORCA needs geographic reasoning.

---

# 6. PostgreSQL + PostGIS

The architecture is:

```text
PostgreSQL
    |
    └── PostGIS
```

PostGIS does not replace PostgreSQL.

Instead:

```text
PostgreSQL = relational database
PostGIS    = geospatial extension
```

---

# 7. Qdrant

Qdrant is ORCA's vector database.

It stores vector embeddings for RAG.

Conceptually:

```text
Document
   ↓
Chunk
   ↓
Embedding
   ↓
Qdrant
```

Qdrant is optimized for semantic similarity search.

---

# 8. What Goes Into Qdrant

Potential knowledge sources include:

```text
Marine advisories
Safety guidelines
Government documents
Operational manuals
Marine regulations
Dataset documentation
Technical documentation
Historical textual information
```

The final ingestion sources are controlled by the RAG/data-source architecture.

---

# 9. What Does NOT Go Into Qdrant

Do not use Qdrant as the main database for:

```text
Users
Passwords
Transactions
Routes
Geofences
Marine coordinates
Application configuration
```

Those belong in PostgreSQL/PostGIS when persistent structured storage is required.

---

# 10. MinIO

MinIO is ORCA's object-storage layer.

It is intended for large files and binary objects.

Examples:

```text
Satellite imagery
Raster datasets
NetCDF files
GeoTIFF files
CSV files
Excel files
PDF documents
Raw downloaded datasets
Processed dataset files
Generated reports
```

---

# 11. What Does NOT Go Into MinIO

Do not use MinIO as the primary store for:

```text
Users
Agent state
Geofences
Risk records
Conversation metadata
```

Those belong in PostgreSQL where relational persistence is required.

---

# 12. Redis

Redis is the fast temporary/cache layer.

Typical uses:

```text
API response caching
Weather-data caching
Marine-data caching
Rate limiting
Temporary workflow state
Short-lived sessions
Task locks
Frequently accessed configuration
```

---

# 13. What Does NOT Go Into Redis

Redis should not be the authoritative permanent database for:

```text
Users
Historical marine observations
Permanent risk assessments
Geofences
Routes
Audit records
Documents
```

Redis data should generally be considered disposable unless a specific persistence requirement exists.

---

# 14. Data Classification

Every piece of ORCA data should first be classified:

```text
                    DATA
                      |
      ┌───────────────┼───────────────┐
      ↓               ↓               ↓
 Structured        Semantic         Large
      |               |               |
 PostgreSQL         Qdrant           MinIO
      |
 Geospatial → PostGIS

Fast temporary data → Redis
```

---

# 15. Core PostgreSQL Domains

The database is logically divided into major domains:

```text
1. Identity
2. Conversation
3. Agent Execution
4. Data Catalog
5. Marine Data
6. Weather Data
7. Ocean Data
8. Geospatial
9. Risk
10. Routing
11. Alerts
12. RAG Metadata
13. Audit
```

---

# 16. Identity Domain

Primary table:

```text
users
```

Purpose:

Store ORCA user accounts.

Conceptual fields:

```text
id
name
email
password_hash
preferred_language
created_at
updated_at
```

Passwords must only be stored as secure password hashes.

---

# 17. Conversation Domain

Main tables:

```text
conversations
messages
```

Relationship:

```text
User
 |
 └── Conversation
       |
       ├── Message
       ├── Message
       └── Message
```

---

# 18. Conversations

Conceptual fields:

```text
id
user_id
title
created_at
updated_at
```

---

# 19. Messages

Conceptual fields:

```text
id
conversation_id
role
content
created_at
```

Possible roles:

```text
user
assistant
system
```

Agent/internal events should not necessarily be exposed as ordinary conversation messages.

---

# 20. Task Domain

A user request may create an ORCA task.

Main table:

```text
tasks
```

Conceptual fields:

```text
id
conversation_id
request_text
status
created_at
started_at
completed_at
```

---

# 21. Task Status

Possible states:

```text
PENDING
PLANNING
RUNNING
COMPLETED
FAILED
CANCELLED
```

---

# 22. Agent Execution Domain

Main table:

```text
agent_runs
```

Conceptual fields:

```text
id
task_id
agent_name
status
started_at
completed_at
duration_ms
retry_count
```

---

# 23. Agent Run Relationship

```text
Task
 |
 ├── Planner Agent Run
 ├── Weather Agent Run
 ├── Ocean Agent Run
 ├── Geospatial Agent Run
 ├── Risk Agent Run
 └── RAG Agent Run
```

---

# 24. Tool Execution

A separate table may be used:

```text
tool_runs
```

Conceptual fields:

```text
id
agent_run_id
tool_name
status
started_at
completed_at
duration_ms
error_type
```

This allows:

```text
Task
 ↓
Agent
 ↓
Tool
```

to be traced.

---

# 25. Dataset Catalog

ORCA needs a catalog describing available datasets.

Main table:

```text
datasets
```

Conceptual fields:

```text
id
name
description
provider
dataset_type
source_url
update_frequency
spatial_coverage
temporal_coverage
created_at
updated_at
```

---

# 26. Dataset Types

Examples:

```text
WEATHER
OCEAN
SATELLITE
MARINE
GEOSPATIAL
ADVISORY
BOUNDARY
DOCUMENT
```

---

# 27. Dataset Freshness

Dataset metadata should track:

```text
last_ingested_at
latest_data_timestamp
freshness_status
last_ingestion_status
```

Possible status:

```text
FRESH
AGING
STALE
UNAVAILABLE
```

---

# 28. Data Sources

Where appropriate, dataset records should identify:

```text
provider
source
API
file
satellite
government portal
```

This is important for evidence and provenance.

---

# 29. Marine Observation Domain

A marine observation may contain:

```text
observation
location
timestamp
measurement
source
```

Examples:

```text
Sea Surface Temperature
Wave Height
Wave Period
Wind Speed
Sea Level
Chlorophyll
Salinity
```

---

# 30. Marine Observations Table

Conceptual table:

```text
marine_observations
```

Fields may include:

```text
id
dataset_id
observation_time
location
parameter
value
unit
source
created_at
```

The exact parameter model will be finalized during schema implementation.

---

# 31. Geospatial Location

Marine observations should use PostGIS geometry/geography types where appropriate.

Example:

```text
location GEOGRAPHY(POINT, 4326)
```

This allows geographic calculations.

---

# 32. Weather Domain

Potential table:

```text
weather_observations
```

Conceptual fields:

```text
id
dataset_id
observation_time
location
temperature
wind_speed
wind_direction
pressure
humidity
precipitation
visibility
```

The exact fields depend on the selected weather sources.

---

# 33. Forecast Data

Forecast information should be distinguished from historical observations.

Potential table:

```text
weather_forecasts
```

Conceptual fields:

```text
id
dataset_id
forecast_generated_at
forecast_time
location
variable
value
unit
```

This distinction is important because:

```text
Observed ≠ Forecast
```

---

# 34. Ocean Analytics

Derived ocean indicators may be stored separately from raw observations.

Potential table:

```text
ocean_indicators
```

Examples:

```text
chlorophyll index
SST anomaly
productivity indicator
fishing suitability score
```

These are derived values and should retain provenance.

---

# 35. Derived Data Principle

ORCA should distinguish:

```text
RAW OBSERVATION
      ↓
PROCESSING
      ↓
DERIVED INDICATOR
      ↓
DECISION
```

Derived information should never be confused with raw observations.

---

# 36. Geospatial Domain

Core geospatial tables may include:

```text
geofences
marine_boundaries
protected_areas
restricted_zones
coastal_regions
fishing_zones
```

---

# 37. Geofences

Main table:

```text
geofences
```

Conceptual fields:

```text
id
name
type
description
geometry
status
source
created_at
updated_at
```

Geometry:

```text
POLYGON
MULTIPOLYGON
```

depending on the source.

---

# 38. Geofence Types

Examples:

```text
INTERNATIONAL_BOUNDARY
RESTRICTED_WATER
MARINE_PROTECTED_AREA
ECOLOGICALLY_SENSITIVE_ZONE
OPERATIONAL_BOUNDARY
CUSTOM_ALERT_ZONE
```

---

# 39. Spatial Queries

PostGIS should answer queries such as:

```text
Is this vessel position inside a restricted zone?

Which protected areas intersect this route?

How far is this fishing location from an international boundary?

Which geofences are within 10 km?
```

---

# 40. Risk Domain

Main table:

```text
risk_assessments
```

Conceptual fields:

```text
id
task_id
location
assessment_time
risk_level
risk_score
factors
created_at
```

---

# 41. Risk Levels

Recommended:

```text
LOW
MODERATE
HIGH
SEVERE
UNKNOWN
```

`UNKNOWN` is important when required information is unavailable.

---

# 42. Risk Factors

Risk should be decomposable.

Example:

```text
risk_assessment
 |
 ├── wind risk
 ├── wave risk
 ├── lightning risk
 ├── cyclone risk
 ├── visibility risk
 └── geofence risk
```

The final schema may normalize these factors or store a structured JSON representation where appropriate.

---

# 43. Recommendation Domain

A recommendation should have provenance.

Potential table:

```text
recommendations
```

Conceptual fields:

```text
id
task_id
risk_assessment_id
recommendation
confidence
created_at
```

---

# 44. Recommendation Evidence

Potential table:

```text
recommendation_evidence
```

Conceptual fields:

```text
id
recommendation_id
source_type
source_id
evidence
timestamp
```

This enables:

```text
Recommendation
      ↓
Evidence
      ↓
Source
```

---

# 45. Routing Domain

Main table:

```text
routes
```

Conceptual fields:

```text
id
task_id
start_location
destination
route_geometry
distance
estimated_duration
risk_score
created_at
```

Route geometry should use PostGIS.

---

# 46. Route Segments

Where detailed routing is required:

```text
route_segments
```

can contain:

```text
route_id
sequence
geometry
distance
risk_score
conditions
```

This allows different portions of a route to have different risk values.

---

# 47. Alerts Domain

Main table:

```text
alerts
```

Conceptual fields:

```text
id
type
severity
title
description
location
valid_from
valid_until
source
status
created_at
```

---

# 48. Alert Types

Examples:

```text
CYCLONE
LIGHTNING
HIGH_WAVES
STRONG_WIND
HEAVY_RAIN
POOR_VISIBILITY
RESTRICTED_ZONE
GEOSPATIAL_BOUNDARY
OTHER_MARINE_HAZARD
```

---

# 49. Alert Lifecycle

```text
CREATED
ACTIVE
EXPIRED
CANCELLED
```

---

# 50. Alert Geospatial Queries

PostGIS can determine:

```text
Which users/locations are inside the alert area?

Which routes intersect the alert?

Which fishing zones are affected?
```

---

# 51. RAG Metadata

The actual embeddings belong in Qdrant.

PostgreSQL should store metadata describing indexed documents.

Potential table:

```text
documents
```

Conceptual fields:

```text
id
title
source
document_type
source_url
storage_object_key
created_at
updated_at
```

---

# 52. Document Chunks

Potential table:

```text
document_chunks
```

Conceptual fields:

```text
id
document_id
chunk_index
text_hash
qdrant_point_id
created_at
```

The actual vector is stored in Qdrant.

---

# 53. RAG Architecture

```text
Document
   |
   ↓
MinIO
   |
   ↓
Text Extraction
   |
   ↓
Chunking
   |
   ↓
Embedding
   |
   ↓
Qdrant
   |
   ↓
PostgreSQL metadata
```

---

# 54. Vector Metadata

Qdrant payload should contain enough metadata to filter and identify retrieved information.

Examples:

```text
document_id
chunk_id
document_type
source
date
region
topic
```

---

# 55. Audit Domain

Main table:

```text
audit_events
```

Conceptual fields:

```text
id
event_type
actor
resource_type
resource_id
timestamp
metadata
```

---

# 56. Audit Purpose

Audit records help answer:

```text
Who performed an operation?

What happened?

When did it happen?

Which resource was affected?
```

---

# 57. Database Relationships

High-level relationship:

```text
User
 |
 └── Conversation
       |
       └── Task
             |
             ├── Agent Runs
             │      |
             │      └── Tool Runs
             |
             ├── Risk Assessment
             |
             ├── Recommendation
             │      |
             │      └── Evidence
             |
             └── Route
```

---

# 58. Dataset Relationships

```text
Dataset
 |
 ├── Marine Observations
 ├── Weather Observations
 ├── Forecasts
 └── Derived Indicators
```

---

# 59. Geospatial Relationships

```text
Geofence
   |
   ├── Restricted Zone
   ├── Protected Area
   ├── Boundary
   └── Fishing Zone
```

All important geographic boundaries should use spatially indexed PostGIS geometry.

---

# 60. PostgreSQL Indexing

Indexes should be created for frequently queried fields.

Examples:

```text
user_id
conversation_id
task_id
dataset_id
timestamp
status
```

---

# 61. PostGIS Spatial Indexes

Spatial columns should use appropriate spatial indexes.

Conceptually:

```text
GIST INDEX
```

for important geometry/geography columns.

This is critical for efficient:

```text
distance queries
intersection queries
containment queries
geofence queries
```

---

# 62. Time Indexing

Marine and weather observations are heavily time-dependent.

Indexes should support:

```text
location
timestamp
dataset
```

queries.

For very large datasets, partitioning can be considered.

---

# 63. Large-Scale Data

If observation volumes become very large:

```text
Partitioning
Time-based partitions
Spatial indexing
Aggregated tables
Materialized views
```

may be introduced.

Do not prematurely complicate the schema before actual volume requires it.

---

# 64. Transactions

PostgreSQL transactions should be used for operations requiring atomicity.

Example:

```text
Create task
+
Create initial task state
+
Create audit event
```

should be handled consistently.

---

# 65. Foreign Keys

Relational integrity should be enforced where appropriate.

Example:

```text
messages.conversation_id
        ↓
conversations.id
```

and:

```text
agent_runs.task_id
        ↓
tasks.id
```

---

# 66. Data Provenance

Important observations and derived values should retain:

```text
source
dataset
timestamp
processing version
```

where applicable.

This is essential for explainability.

---

# 67. Observation Provenance

Conceptually:

```text
Observation
    |
    ├── Dataset
    ├── Source
    ├── Observation Time
    └── Ingestion Time
```

---

# 68. Decision Provenance

Conceptually:

```text
Recommendation
      |
      ├── Risk Assessment
      |
      ├── Observations
      |
      ├── Forecasts
      |
      ├── Geospatial Constraints
      |
      └── Evidence
```

---

# 69. Cache Strategy

Redis should cache frequently requested data.

Examples:

```text
Weather for location X
Marine conditions for location Y
Frequently requested geospatial results
External API responses
```

Cache entries must have TTLs.

---

# 70. Cache Invalidation

Cache data should expire automatically where possible.

Concept:

```text
External Data
     ↓
Redis
     ↓
TTL expires
     ↓
Fresh data retrieved
```

Do not allow stale cached data to silently override authoritative fresh information.

---

# 71. Cache Keys

Use consistent key naming.

Example:

```text
orca:weather:{location}:{time}
orca:marine:{location}:{time}
orca:risk:{location}:{time}
```

The exact scheme will be finalized during implementation.

---

# 72. Redis Locks

Redis may be used for distributed/temporary locks where necessary.

Example:

```text
Dataset ingestion
      |
      ↓
Acquire lock
      |
      ↓
Run ingestion
      |
      ↓
Release lock
```

This prevents duplicate concurrent jobs.

---

# 73. MinIO Bucket Strategy

Logical buckets may include:

```text
orca-raw
orca-processed
orca-documents
orca-reports
```

Exact bucket naming may be changed during deployment.

---

# 74. MinIO Object Naming

Objects should use predictable paths.

Example:

```text
satellite/
    2026/
       08/
          dataset/
```

or:

```text
documents/
    advisories/
    regulations/
```

---

# 75. Database Backup

PostgreSQL backups should be performed using standard PostgreSQL backup mechanisms.

Development backups should be stored on:

```text
D:\
```

where appropriate.

---

# 76. Database Migrations

Schema changes must be version-controlled using:

```text
Alembic
```

Example:

```text
migration 001
migration 002
migration 003
```

---

# 77. Development Database

Development should use a dedicated database:

```text
orca_db
```

Do not mix ORCA tables into unrelated project databases.

---

# 78. Production Separation

Development and production databases must be separate.

Never point local development code at a production database.

---

# 79. Database Security

Credentials must be stored in environment variables/secrets.

Never hardcode:

```text
database passwords
API keys
MinIO secret keys
Redis credentials
```

---

# 80. Connection Pooling

The backend should use database connection pooling rather than opening a new PostgreSQL connection for every request.

---

# 81. Database Health

The backend health system should verify PostgreSQL connectivity.

Example:

```text
PostgreSQL
    ↓
SELECT 1
    ↓
Healthy
```

---

# 82. Redis Health

Redis health should similarly be checked through an appropriate lightweight operation.

---

# 83. Qdrant Health

The backend should verify Qdrant availability before executing RAG workflows requiring it.

---

# 84. MinIO Health

Object storage availability should be checked before file-dependent workflows.

---

# 85. Database Failure Behavior

If PostgreSQL is unavailable:

```text
Do not fabricate persistent results.
```

The application should return an appropriate controlled error.

---

# 86. Vector Database Failure

If Qdrant is unavailable:

```text
RAG retrieval unavailable
```

The system should clearly distinguish this from:

```text
No relevant documents found
```

---

# 87. Object Storage Failure

If MinIO is unavailable:

```text
File retrieval unavailable
```

The application should not pretend that the file was successfully retrieved.

---

# 88. Data Consistency

ORCA must distinguish:

```text
Source Data
Derived Data
Cached Data
Retrieved Evidence
Final Recommendation
```

These should not be conflated.

---

# 89. Database Architecture Summary

```text
                         ORCA
                           |
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
       PostgreSQL        Qdrant         MinIO
             |
          PostGIS
             |
       Structured +
       Geospatial
```

Parallel fast-access layer:

```text
Redis
  |
  ├── Cache
  ├── Temporary state
  └── Locks
```

---

# 90. Complete Data Flow

```text
External Sources
      |
      ↓
Data Ingestion
      |
      ├──────────────→ MinIO
      |
      └──────────────→ PostgreSQL/PostGIS
                              |
                              ↓
                       Data Processing
                              |
                              ↓
                       Derived Indicators
                              |
                              ↓
                         Risk Engine
                              |
                              ↓
                       Recommendation
```

RAG:

```text
Documents
   ↓
MinIO
   ↓
Extraction
   ↓
Chunking
   ↓
Embeddings
   ↓
Qdrant
   ↓
Retrieval
   ↓
LLM
```

Cache:

```text
External APIs
     ↓
   Redis
     ↓
 Fast retrieval
```

---

# 91. Final Storage Decision

ORCA officially uses:

```text
POSTGRESQL
→ Primary structured database

POSTGIS
→ Geospatial extension for PostgreSQL

REDIS
→ Cache + temporary high-speed state

QDRANT
→ Vector database / RAG retrieval

MINIO
→ Object storage / large files
```

---

# 92. What We Are NOT Adding

At the current architecture stage, ORCA does NOT require another database such as:

```text
MongoDB
MySQL
SQLite
Neo4j
Elasticsearch
```

unless a future architectural requirement explicitly justifies it.

Adding databases without a specific purpose would increase complexity without improving ORCA.

---

# 93. Frozen Database Principles

1. PostgreSQL is the primary persistent relational database.
2. PostGIS handles geospatial operations.
3. Redis is not the source of truth.
4. Qdrant is dedicated to vector retrieval.
5. MinIO stores large objects and files.
6. Structured data belongs in PostgreSQL.
7. Geospatial data belongs in PostgreSQL/PostGIS.
8. Embeddings belong in Qdrant.
9. Large binary files belong in MinIO.
10. Temporary/cache data belongs in Redis.
11. Important data must retain provenance.
12. Raw and derived data must remain distinguishable.
13. Cached data must have appropriate expiration.
14. Database schema changes must use migrations.
15. Spatial columns must use appropriate spatial indexes.
16. Time-series-like observations must be designed for efficient temporal queries.
17. Production and development databases must remain isolated.
18. Secrets must never be stored in source code.
19. Database failures must produce explicit system states.
20. ORCA must never fabricate missing database or data-source results.

---

# 94. Final Architecture

```text
                        ORCA
                         |
              ┌──────────┼──────────┐
              ↓          ↓          ↓
        PostgreSQL     Qdrant      MinIO
              |
           PostGIS
              |
       ┌──────┼──────┐
       ↓      ↓      ↓
   App Data Marine  Geo Data
              |
              ↓
         Risk / Route
              |
              ↓
       Recommendation
              |
              ↓
          Evidence


             Redis
               |
       Cache / Temp State
```

---

# 95. Status

This document freezes the baseline ORCA database architecture.

Future implementation may refine:

* exact table names
* exact columns
* indexes
* partitioning
* bucket names
* Qdrant collections
* Redis key structure
* retention policies
