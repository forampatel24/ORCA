# ORCA — Database & Storage Design

**Project Name:** ORCA  
**Document:** Database & Storage Design  
**Document ID:** ORCA-DB-05  
**Version:** 1.0  
**Status:** FROZEN BASELINE  
**Scope:** Complete ORCA System

---

# 1. Database Architecture

ORCA uses four specialized storage systems:

1. PostgreSQL
2. PostGIS
3. Redis
4. MinIO
5. Qdrant

PostGIS is an extension of PostgreSQL, not a separate standalone database.

Therefore:

```text
                    ORCA STORAGE
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
 PostgreSQL           Redis             MinIO
        │
     PostGIS
        │
        └─────────────────────┐
                              │
                              ▼
                           Qdrant
````

---

# 2. Responsibility of Each System

| Storage    | Primary Responsibility                          |
| ---------- | ----------------------------------------------- |
| PostgreSQL | Structured relational application data          |
| PostGIS    | Spatial/geographic data and spatial computation |
| Redis      | Cache, transient state, fast-access data        |
| MinIO      | Large files and object storage                  |
| Qdrant     | Vector embeddings and semantic retrieval        |

---

# 3. PostgreSQL

PostgreSQL is ORCA's authoritative relational database.

It stores structured application-level information.

Examples:

```text
Users
Conversations
Messages
Agent executions
Tool executions
Alerts
Risk assessments
Routes
Data source metadata
System configuration
```

---

# 4. PostGIS

PostGIS is enabled inside PostgreSQL.

It stores geographic objects and enables spatial computation.

Examples:

```text
PFZ locations
Vessel locations
Hazard geometries
Geofences
Marine protected areas
Maritime boundaries
Routes
Coastlines
```

---

# 5. Redis

Redis is not the permanent source of truth.

It is used for:

```text
Caching
Temporary state
Rate limiting
Short-lived workflow information
Frequently requested data
Background job support
```

If Redis is cleared, the permanent application data must remain available through PostgreSQL/PostGIS/MinIO/Qdrant.

---

# 6. MinIO

MinIO provides S3-compatible object storage.

It is used for large files.

Examples:

```text
PDFs
Satellite files
Raster files
NetCDF files
GeoTIFF files
Uploaded documents
Raw datasets
Processed dataset artifacts
```

Large binary files should not unnecessarily be stored directly inside PostgreSQL.

---

# 7. Qdrant

Qdrant is the vector database for the RAG system.

It stores:

```text
Document embeddings
Chunk embeddings
Metadata associated with chunks
```

It enables:

```text
Semantic Search
Similarity Search
RAG Retrieval
```

Qdrant is not the authoritative source for marine measurements.

---

# 8. PostgreSQL Schema

The relational database shall be logically organized into domains.

```text
PostgreSQL
│
├── auth
├── conversation
├── agents
├── data
├── risk
├── routing
├── alerts
└── system
```

The implementation may use PostgreSQL schemas or a unified schema with table prefixes depending on implementation requirements.

---

# 9. Users Table

```text
users
```

Purpose:

Stores registered ORCA users.

Suggested fields:

```text
id
email
password_hash
name
preferred_language
created_at
updated_at
is_active
```

---

# 10. User Preferences

```text
user_preferences
```

Purpose:

Stores user-specific application preferences.

Possible fields:

```text
id
user_id
preferred_language
notification_enabled
alert_preferences
default_location
created_at
updated_at
```

Location-related fields that require spatial querying should use PostGIS-compatible geometry types where appropriate.

---

# 11. Conversations Table

```text
conversations
```

Purpose:

Stores conversation sessions.

Fields:

```text
id
user_id
title
created_at
updated_at
```

Relationship:

```text
User
 │
 └──< Conversations
```

---

# 12. Messages Table

```text
messages
```

Purpose:

Stores conversation messages.

Fields:

```text
id
conversation_id
role
content
language
created_at
```

Possible roles:

```text
user
assistant
system
```

Relationship:

```text
Conversation
      │
      └──< Messages
```

---

# 13. Agent Runs Table

```text
agent_runs
```

Purpose:

Tracks agent executions.

Fields:

```text
id
conversation_id
agent_name
status
input
output
started_at
completed_at
error
```

Possible statuses:

```text
pending
running
completed
failed
```

This is useful for:

* Debugging
* Evaluation
* Observability
* Demonstrating agentic workflows

---

# 14. Tool Runs Table

```text
tool_runs
```

Purpose:

Tracks tool execution.

Fields:

```text
id
agent_run_id
tool_name
input
output
status
started_at
completed_at
error
```

Relationship:

```text
Conversation
    │
    ▼
Agent Run
    │
    └──< Tool Runs
```

---

# 15. Data Sources Table

```text
data_sources
```

Purpose:

Maintains metadata about external data sources.

Fields:

```text
id
name
source_type
provider
endpoint
update_frequency
last_updated
status
metadata
```

Examples of source types:

```text
marine
weather
satellite
fisheries
geospatial
knowledge
```

---

# 16. Data Ingestion Runs

```text
ingestion_runs
```

Purpose:

Tracks data ingestion processes.

Fields:

```text
id
data_source_id
started_at
completed_at
status
records_processed
records_inserted
records_updated
records_failed
error
```

---

# 17. PFZ Data

```text
pfz_observations
```

Purpose:

Stores Potential Fishing Zone information.

Possible fields:

```text
id
source_id
observation_time
valid_from
valid_to
latitude
longitude
geometry
metadata
created_at
```

The spatial representation should use PostGIS.

Example:

```text
geometry GEOGRAPHY(POINT, 4326)
```

or an appropriate geometry type depending on the actual PFZ product.

---

# 18. Ocean Observations

```text
ocean_observations
```

Possible fields:

```text
id
source_id
observation_time
location
sst
chlorophyll
wave_height
wave_period
wind_speed
current_speed
metadata
```

The exact columns depend on the actual source datasets.

---

# 19. Weather Observations

```text
weather_observations
```

Possible fields:

```text
id
source_id
observation_time
forecast_time
location
temperature
wind_speed
wind_direction
rainfall
humidity
pressure
metadata
```

---

# 20. Hazard Data

```text
marine_hazards
```

Possible fields:

```text
id
source_id
hazard_type
severity
valid_from
valid_to
geometry
description
metadata
```

Possible hazard types:

```text
cyclone
lightning
high_wave
strong_wind
heavy_rain
dangerous_current
other
```

---

# 21. Cyclone Data

```text
cyclones
```

Possible fields:

```text
id
source_id
name
observation_time
forecast_time
center_location
wind_speed
pressure
category
track_geometry
metadata
```

The track should use an appropriate PostGIS geometry.

---

# 22. Geofence Table

```text
geofences
```

Purpose:

Stores operational boundaries.

Possible fields:

```text
id
name
geofence_type
geometry
severity
description
active
metadata
```

Types may include:

```text
restricted
protected
boundary
operational
warning
```

---

# 23. Marine Protected Areas

```text
protected_areas
```

Possible fields:

```text
id
name
area_type
geometry
authority
restrictions
description
metadata
```

---

# 24. Maritime Boundaries

```text
maritime_boundaries
```

Possible fields:

```text
id
name
boundary_type
geometry
country
description
metadata
```

---

# 25. Vessel Locations

```text
vessel_positions
```

Possible fields:

```text
id
vessel_id
timestamp
location
speed
heading
source
metadata
```

The exact implementation depends on the availability and authorization of vessel data.

---

# 26. Risk Assessments

```text
risk_assessments
```

Stores deterministic risk-analysis results.

Fields:

```text
id
user_id
location
assessment_time
valid_from
valid_to
risk_score
risk_level
risk_factors
data_quality
created_at
```

Example:

```json
{
  "risk_score": 72,
  "risk_level": "HIGH",
  "risk_factors": [
    "High wave conditions",
    "Strong wind",
    "Lightning activity"
  ]
}
```

---

# 27. Routes

```text
routes
```

Stores generated route information.

Fields:

```text
id
user_id
origin
destination
route_geometry
distance
estimated_duration
risk_score
route_score
created_at
metadata
```

`route_geometry` should use PostGIS.

---

# 28. Alerts

```text
alerts
```

Stores generated alerts.

Fields:

```text
id
user_id
alert_type
severity
title
message
location
valid_from
valid_to
source
status
created_at
```

Possible types:

```text
weather
cyclone
lightning
wave
geofence
marine
route
```

---

# 29. Alert Events

```text
alert_events
```

Used for tracking alert delivery/evaluation.

Possible fields:

```text
id
alert_id
event_type
triggered_at
delivered_at
acknowledged_at
status
metadata
```

---

# 30. Route Constraints

```text
route_constraints
```

Stores configurable routing constraints.

Possible fields:

```text
id
constraint_type
value
geometry
priority
active
metadata
```

Examples:

```text
avoid protected area
avoid restricted area
maximum wave height
maximum wind speed
```

---

# 31. Knowledge Documents

Metadata for RAG documents should be stored in PostgreSQL.

```text
knowledge_documents
```

Fields:

```text
id
title
source
document_type
object_storage_key
language
version
created_at
updated_at
metadata
```

The actual document file belongs in MinIO.

---

# 32. Knowledge Chunks

```text
knowledge_chunks
```

Stores metadata about document chunks.

Fields:

```text
id
document_id
chunk_index
text
language
embedding_id
metadata
created_at
```

The vector itself is stored in Qdrant.

---

# 33. Database Relationship Overview

```text
USER
 │
 ├──< CONVERSATIONS
 │       │
 │       └──< MESSAGES
 │
 ├──< ALERTS
 │
 ├──< RISK_ASSESSMENTS
 │
 └──< ROUTES


CONVERSATION
 │
 └──< AGENT_RUNS
          │
          └──< TOOL_RUNS


DATA_SOURCE
 │
 └──< INGESTION_RUNS


KNOWLEDGE_DOCUMENT
 │
 └──< KNOWLEDGE_CHUNKS
```

---

# 34. Spatial Database Design

All spatial data shall use an appropriate coordinate reference system.

For global geographic coordinates, the standard geographic CRS will generally be:

```text
EPSG:4326
```

The actual storage type shall be selected according to the operation:

```text
GEOGRAPHY
```

or

```text
GEOMETRY
```

---

# 35. Spatial Indexes

Spatial columns shall use spatial indexes where appropriate.

Example concept:

```sql
CREATE INDEX idx_geofences_geometry
ON geofences
USING GIST (geometry);
```

This enables efficient spatial queries.

---

# 36. Important PostGIS Operations

ORCA will use spatial operations such as:

```text
ST_DWithin
ST_Distance
ST_Intersects
ST_Contains
ST_Within
ST_Buffer
ST_Transform
```

Examples:

```text
Find PFZs within 50 km
Check whether a vessel is inside a restricted zone
Check whether a route intersects a protected area
Find nearest fishing zone
Calculate distance to boundary
```

---

# 37. Redis Data Design

Redis keys should be namespaced.

Example:

```text
orca:weather:{location}:{time}
orca:ocean:{location}:{time}
orca:pfz:{region}:{date}
orca:session:{session_id}
orca:rate_limit:{user_id}
```

---

# 38. Redis TTL

Cached data should have a Time-To-Live appropriate to its freshness requirements.

Example:

```text
Weather → short TTL
Frequently changing marine data → short TTL
Historical static data → longer TTL
Reference metadata → longer TTL
```

Exact TTL values shall be configured later according to the actual source update frequency.

---

# 39. MinIO Bucket Architecture

MinIO shall use logically separated buckets.

Suggested structure:

```text
orca-documents
orca-raw-data
orca-satellite
orca-raster
orca-processed
orca-artifacts
```

---

# 40. MinIO Object Structure

Example:

```text
orca-documents/
    advisories/
    regulations/
    safety/
    scientific/

orca-satellite/
    source/
    date/
    product/

orca-raster/
    sst/
    chlorophyll/
    bathymetry/
```

The exact organization may evolve according to ingestion requirements.

---

# 41. Qdrant Collection Architecture

Qdrant collections should be separated according to logical knowledge domains when beneficial.

Possible collections:

```text
marine_knowledge
safety_knowledge
regulations
fisheries_knowledge
scientific_knowledge
```

Alternatively, a unified collection with metadata filtering may be used.

The final strategy shall depend on retrieval evaluation.

---

# 42. Qdrant Metadata

Each vector should retain metadata such as:

```text
document_id
chunk_id
source
document_type
language
date
topic
authority
```

This enables filtered retrieval.

Example:

```text
Query
 ↓
Qdrant
 ↓
Filter:
language = English
document_type = advisory
topic = fishing safety
 ↓
Relevant chunks
```

---

# 43. RAG Storage Flow

```text
                 DOCUMENT
                    │
                    ▼
                  MinIO
                    │
                    ▼
                 Parser
                    │
                    ▼
                  Chunks
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     PostgreSQL            Embedding
     Metadata                  │
          │                    ▼
          │                  Qdrant
          │                    │
          └─────────┬──────────┘
                    ▼
                Retrieval
                    │
                    ▼
                 Evidence
```

---

# 44. Large Data Storage Strategy

Large datasets should not automatically be inserted row-by-row into PostgreSQL.

The storage strategy should depend on the data type.

```text
Small structured data
        ↓
PostgreSQL/PostGIS

Large files
        ↓
MinIO

Multidimensional scientific data
        ↓
MinIO + processing pipeline

Semantic knowledge
        ↓
MinIO + PostgreSQL metadata + Qdrant
```

---

# 45. Data Provenance

Each important dataset record should retain provenance where possible.

Metadata should include:

```text
source
provider
observation time
ingestion time
validity
processing version
dataset/product identifier
```

This allows ORCA to answer:

```text
"Where did this information come from?"
```

---

# 46. Data Freshness

The database design distinguishes:

```text
Observation Time
Forecast Time
Valid From
Valid To
Ingestion Time
```

These must not be treated as interchangeable.

Example:

```text
Data downloaded:
10:00

Forecast valid for:
18:00

These are two different timestamps.
```

---

# 47. Data Lifecycle

The data lifecycle is:

```text
External Source
      ↓
Ingestion
      ↓
Validation
      ↓
Normalization
      ↓
Storage
      ↓
Indexing
      ↓
Caching
      ↓
Agent Retrieval
      ↓
Analysis
      ↓
Response
```

---

# 48. Database Access Architecture

Agents shall not directly manipulate databases wherever possible.

Instead:

```text
Agent
  ↓
Tool
  ↓
Service
  ↓
Repository / Data Access Layer
  ↓
Database
```

Example:

```text
Marine Data Agent
       ↓
get_pfz()
       ↓
PFZ Service
       ↓
PostGIS Repository
       ↓
PostgreSQL/PostGIS
```

This keeps the agent layer independent of database implementation details.

---

# 49. Transaction Strategy

PostgreSQL transactions shall be used for operations that require atomicity.

Examples:

```text
Create alert + alert event
Store conversation message + metadata
Create route + route metadata
Record ingestion result
```

---

# 50. Database Security

Database credentials shall never be committed to source control.

Credentials shall be provided through environment configuration.

Example:

```text
DATABASE_URL
REDIS_URL
MINIO_ACCESS_KEY
MINIO_SECRET_KEY
QDRANT_URL
```

---

# 51. Backup Strategy

Persistent data shall be backed up according to its importance.

Priority:

```text
PostgreSQL/PostGIS
        ↓
High

MinIO
        ↓
High

Qdrant
        ↓
Rebuildable but important

Redis
        ↓
Generally disposable
```

Qdrant vectors should be reproducible from the original documents and embedding pipeline where practical.

---

# 52. What Goes Where

This is the most important practical rule.

## PostgreSQL

```text
Users
Conversations
Messages
Agents
Tool executions
Alerts
Risk assessments
Routes
Data-source metadata
Document metadata
```

## PostGIS

```text
PFZ coordinates
Vessel positions
Hazards
Geofences
Protected areas
Maritime boundaries
Route geometry
Spatial observations
```

## Redis

```text
Cache
Temporary state
Rate limits
Short-lived data
Fast-access results
```

## MinIO

```text
PDFs
Satellite files
Raster files
NetCDF
GeoTIFF
Raw datasets
Processed artifacts
```

## Qdrant

```text
Embeddings
Semantic-search vectors
RAG retrieval metadata
```

---

# 53. What NOT to Do

ORCA shall avoid the following architecture mistakes.

### Do not store everything in PostgreSQL

Large files belong in MinIO.

---

### Do not store everything in Redis

Redis is not the primary permanent database.

---

### Do not store raw PDFs inside Qdrant

Qdrant stores vectors and retrieval metadata.

---

### Do not use Qdrant for numerical marine observations

Marine measurements belong in structured data storage.

---

### Do not ask the LLM to perform GIS calculations

Use PostGIS/geometry libraries.

---

### Do not ask the LLM to invent route coordinates

Use a deterministic routing system.

---

### Do not treat cached data as authoritative

Redis is a performance layer.

---

# 54. Final Storage Architecture

```text
                         ORCA
                           │
                           ▼
                     DATA SERVICES
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
     PostgreSQL          Redis            MinIO
          │             Cache             Objects
          │
       PostGIS
          │
          └──────────────────────┐
                                 │
                                 ▼
                              Qdrant
                              Vectors
```

---

# 55. Final Decision

ORCA's storage architecture is therefore:

```text
                PostgreSQL
                     │
                  PostGIS
                     │
          ┌──────────┼──────────┐
          │          │          │
        Redis      MinIO      Qdrant
```

with each system having a clearly defined role.

The permanent source of truth is primarily:

```text
PostgreSQL + PostGIS + MinIO
```

The performance layer is:

```text
Redis
```

The semantic retrieval layer is:

```text
Qdrant
```

---

# 56. Database Design Principle

ORCA follows the rule:

```text
STORE ACCORDING TO DATA CHARACTERISTICS.

Structured → PostgreSQL
Spatial → PostGIS
Temporary/Fast → Redis
Large Files → MinIO
Semantic Vectors → Qdrant
```

This separation allows ORCA to handle heterogeneous marine intelligence data without turning one database into a bottleneck or forcing incompatible data types into the wrong storage system.
