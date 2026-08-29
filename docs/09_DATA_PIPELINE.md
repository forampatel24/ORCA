# ORCA — Data Pipeline

**Project Name:** ORCA  
**Document:** Data Pipeline  
**Document ID:** ORCA-DATA-09  
**Version:** 1.0  
**Status:** FROZEN BASELINE  
**Scope:** Data Ingestion, Validation, Processing, Storage, Updating, Caching and Agent Access

---

# 1. Purpose

The ORCA data pipeline converts heterogeneous marine, oceanographic, meteorological, satellite, geospatial and knowledge sources into reliable data that can be consumed by ORCA's agents.

The pipeline must support:

- API-based data
- File-based datasets
- Satellite products
- Raster data
- Scientific multidimensional data
- Geospatial data
- Documents
- Historical datasets
- Forecast datasets
- Near-real-time data

---

# 2. Core Pipeline

ORCA follows:

SOURCE
  ↓
INGEST
  ↓
RAW STORAGE
  ↓
VALIDATE
  ↓
NORMALIZE
  ↓
PROCESS
  ↓
QUALITY CONTROL
  ↓
STRUCTURED STORAGE
  ↓
INDEX
  ↓
AGENT TOOLS
  ↓
ANALYSIS
  ↓
EVIDENCE
  ↓
RESPONSE

---

# 3. Pipeline Architecture

```text
                    EXTERNAL SOURCES
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
      APIs               FILES             SATELLITE
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                    SOURCE CONNECTORS
                           │
                           ▼
                     INGESTION LAYER
                           │
                           ▼
                      RAW STORAGE
                        (MinIO)
                           │
                           ▼
                     VALIDATION
                           │
                           ▼
                    NORMALIZATION
                           │
                           ▼
                      PROCESSING
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        PostgreSQL      PostGIS        MinIO
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                     DATA INDEXING
                           │
                           ▼
                     AGENT TOOL LAYER
                           │
                           ▼
                    MULTI-AGENT SYSTEM
````

---

# 4. Source Connectors

Every external source should have a connector responsible for communicating with that source.

Conceptually:

```text
connector/
├── pfz/
├── weather/
├── ocean/
├── satellite/
├── cyclone/
├── lightning/
├── tides/
├── geospatial/
└── advisories/
```

A connector should handle:

* Authentication
* Request construction
* Pagination
* Downloading
* API errors
* Retries
* Rate limits
* Response parsing
* Source metadata

---

# 5. Connector Contract

Every connector should expose a common conceptual interface.

```python
fetch()
validate_source()
get_metadata()
transform()
```

The exact implementation can differ between sources.

---

# 6. API Ingestion

For API-based datasets:

```text
API
 ↓
HTTP Request
 ↓
Response
 ↓
Schema Validation
 ↓
Normalization
 ↓
Processing
 ↓
Database
```

API failures must not crash the entire ORCA platform.

---

# 7. File Ingestion

For downloaded files:

```text
Dataset File
 ↓
File Validation
 ↓
Checksum / Metadata
 ↓
MinIO Raw Storage
 ↓
Parser
 ↓
Normalization
 ↓
Processing
 ↓
Database / MinIO
```

Supported formats include:

```text
CSV
JSON
GeoJSON
GeoTIFF
NetCDF
HDF
Parquet
PDF
```

---

# 8. Raw Data Storage

Raw external files should be stored before destructive processing whenever practical.

Storage:

```text
MinIO
```

Example:

```text
raw/
├── pfz/
├── satellite/
├── weather/
├── ocean/
├── hazards/
└── documents/
```

This provides:

* Reproducibility
* Auditability
* Reprocessing capability
* Source preservation

---

# 9. Data Validation

Every ingestion operation should perform validation.

Validation categories:

```text
Schema validation
Coordinate validation
Timestamp validation
Unit validation
Null validation
Range validation
Duplicate detection
File integrity
```

---

# 10. Schema Validation

Incoming records must be checked against expected schemas.

Example:

```text
Expected:
latitude
longitude
timestamp
sst
```

If a provider changes:

```text
lat
lon
time
temperature
```

the connector must map the external schema to ORCA's internal schema.

---

# 11. Coordinate Validation

Geospatial records must be checked.

Examples of invalid values:

```text
Latitude > 90
Latitude < -90
Longitude > 180
Longitude < -180
```

Invalid coordinates must not enter the spatial database.

---

# 12. Timestamp Validation

All observations must have a valid timestamp where applicable.

ORCA distinguishes:

```text
Observation Time
Forecast Time
Valid From
Valid Until
Ingestion Time
```

---

# 13. Unit Normalization

Different sources may use different units.

Example:

```text
Kelvin
   ↓
Celsius
```

or:

```text
m/s
   ↓
knots
```

The internal representation should use a consistent standard.

The original source unit should remain available in provenance metadata where useful.

---

# 14. Spatial Normalization

External geographic representations must be converted into compatible spatial representations.

```text
External CRS
     ↓
CRS Detection
     ↓
Validation
     ↓
Transformation
     ↓
PostGIS
```

Global latitude/longitude data should generally use:

```text
EPSG:4326
```

where appropriate.

---

# 15. Temporal Normalization

Time information should be normalized.

Internally ORCA should use timezone-aware timestamps.

Conceptually:

```text
Source Timestamp
      ↓
Parse
      ↓
Timezone Resolution
      ↓
UTC / Internal Standard
```

The original timestamp metadata may be preserved.

---

# 16. Deduplication

The pipeline should detect duplicate observations.

Possible duplicate key:

```text
source
+
dataset
+
location
+
timestamp
+
variable
```

Duplicate handling depends on the source.

---

# 17. Quality Control

After normalization:

```text
Normalized Data
      ↓
Quality Rules
      ↓
Valid?
 ┌────┴────┐
Yes        No
 │          │
 ▼          ▼
Store      Flag
```

Invalid data should not silently become trusted information.

---

# 18. Quality Flags

Measurements can contain:

```text
VALID
SUSPECT
INVALID
MISSING
UNKNOWN
```

Quality flags should be preserved.

---

# 19. Missing Data

Missing values should not automatically be replaced.

The pipeline should distinguish:

```text
Missing
Not Available
Not Applicable
Invalid
```

Imputation should only occur when analytically justified.

---

# 20. Satellite Pipeline

Satellite products may be large and computationally expensive.

The pipeline:

```text
Satellite Source
      ↓
Download
      ↓
MinIO
      ↓
Read Raster / Scientific File
      ↓
Quality Filtering
      ↓
Spatial Processing
      ↓
Temporal Processing
      ↓
Derived Product
      ↓
PostGIS / MinIO
```

---

# 21. Raster Processing

Raster operations may include:

```text
Reprojection
Clipping
Resampling
Masking
Spatial extraction
Aggregation
Quality masking
```

These operations should happen in the processing layer rather than inside the LLM.

---

# 22. NetCDF / HDF Processing

Scientific datasets may contain:

```text
time
latitude
longitude
depth
variable
```

The processing layer should extract the relevant variables and convert them into analytical representations.

---

# 23. Geospatial Processing

Geospatial processing may include:

```text
Spatial joins
Intersection
Containment
Buffering
Distance calculation
Nearest-neighbour search
Geometry simplification
Route intersection
```

PostGIS should perform database-level spatial operations whenever appropriate.

---

# 24. PFZ Pipeline

```text
PFZ Source
   ↓
Ingest
   ↓
Validate coordinates
   ↓
Validate date
   ↓
Normalize geometry
   ↓
PostGIS
   ↓
Spatial Index
   ↓
Marine Agent Tool
```

---

# 25. Weather Pipeline

```text
Weather Source
   ↓
API Retrieval
   ↓
Schema Validation
   ↓
Unit Normalization
   ↓
Temporal Normalization
   ↓
PostgreSQL
   ↓
Spatial Representation
   ↓
Weather Agent Tool
```

---

# 26. Ocean Pipeline

```text
SST / Chlorophyll / Waves / Currents
                ↓
             Ingest
                ↓
            Validation
                ↓
           Normalization
                ↓
        Scientific Processing
                ↓
       PostgreSQL / PostGIS
                ↓
        Ocean Agent Tools
```

---

# 27. Hazard Pipeline

Hazard information follows a high-priority pipeline:

```text
Hazard Source
     ↓
Ingest
     ↓
Validate
     ↓
Normalize
     ↓
Convert to Spatial Geometry
     ↓
PostGIS
     ↓
Hazard Index
     ↓
Risk Agent
     ↓
Alert Agent
```

---

# 28. Geofence Pipeline

Static geofences should be loaded into PostGIS.

```text
Boundary Dataset
      ↓
Geometry Validation
      ↓
CRS Normalization
      ↓
PostGIS
      ↓
Spatial Index
```

---

# 29. Document Pipeline

Documents follow a separate RAG pipeline.

```text
PDF / Document
      ↓
MinIO
      ↓
Text Extraction
      ↓
Cleaning
      ↓
Chunking
      ↓
Metadata
      ↓
Embedding
      ↓
Qdrant
```

---

# 30. Document Metadata

Every document should retain:

```text
document_id
title
source
provider
publication_date
document_type
language
version
ingestion_time
```

This metadata can be stored in PostgreSQL.

---

# 31. Embedding Pipeline

```text
Document
    ↓
Chunks
    ↓
Embedding Model
    ↓
Vector
    ↓
Qdrant
```

Each vector should retain metadata allowing the original document to be identified.

---

# 32. RAG Retrieval

When a knowledge question arrives:

```text
User Query
    ↓
Embedding
    ↓
Qdrant Search
    ↓
Relevant Chunks
    ↓
Evidence
    ↓
RAG Agent
```

---

# 33. Structured Data Retrieval

Numerical and spatial questions should NOT be answered purely through RAG.

Example:

> "Which PFZ is nearest to me?"

Correct:

```text
User Location
      ↓
PostGIS
      ↓
Distance Query
      ↓
Nearest PFZ
```

Not:

```text
User Query
 ↓
Vector Search
 ↓
Guess
```

---

# 34. Hybrid Retrieval

ORCA uses:

```text
Structured Retrieval
        +
Spatial Retrieval
        +
Temporal Retrieval
        +
Vector Retrieval
        +
External APIs
```

This is essential to ORCA's architecture.

---

# 35. Redis Caching

Redis provides temporary high-speed caching.

Potential cache targets:

```text
Weather API responses
Marine conditions
PFZ searches
Frequently requested geospatial queries
Short-lived agent results
```

---

# 36. Cache Flow

```text
Agent Request
     ↓
Redis?
 ┌───┴───┐
Yes      No
 │        │
 ▼        ▼
Return   Source
          ↓
        Process
          ↓
        Redis
          ↓
        Return
```

---

# 37. Cache Expiration

Cache duration must depend on data freshness.

Example:

```text
Real-time hazard
→ very short TTL

Weather forecast
→ source-dependent TTL

Static boundary
→ long TTL

Historical dataset
→ long TTL
```

The cache must never override fresher source data.

---

# 38. Scheduling

ORCA requires scheduled ingestion for datasets that update periodically.

Conceptually:

```text
Scheduler
    ↓
Check Dataset
    ↓
New Data?
    ↓
Ingest
    ↓
Process
    ↓
Store
```

---

# 39. Incremental Updates

The system should avoid downloading unchanged datasets when possible.

Use:

```text
Last Updated Timestamp
ETag
Checksum
Dataset Version
Provider Metadata
```

where supported.

---

# 40. Retry Strategy

Transient failures should be retried.

```text
Request
  ↓
Failure
  ↓
Retry
  ↓
Failure
  ↓
Retry with backoff
  ↓
Failure
  ↓
Mark source degraded
```

Exponential backoff should be used where appropriate.

---

# 41. Source Failure

If one source fails:

```text
Source A → Available
Source B → Failed
Source C → Available
```

ORCA should continue using:

```text
Source A
Source C
```

rather than bringing down the entire platform.

---

# 42. Stale Data

If a source becomes unavailable:

```text
Latest valid data
      ↓
Check age
      ↓
Acceptable?
 ┌────┴────┐
Yes        No
 │          │
Use        Reject /
with       warn
warning
```

The system must disclose when recommendations depend on stale information.

---

# 43. Data Freshness Metadata

Every dataset should track:

```text
source_timestamp
ingestion_timestamp
processing_timestamp
last_successful_update
```

---

# 44. Provenance

Each derived result should maintain provenance.

Example:

```text
Risk Score
   ↓
Weather Forecast
   ↓
Wave Forecast
   ↓
Lightning Data
   ↓
Marine Advisory
```

The user-facing explanation can then reference the underlying evidence.

---

# 45. Agent Tool Interface

Agents should not directly manipulate database internals.

Instead:

```text
Agent
  ↓
Tool
  ↓
Service Layer
  ↓
Database / API
```

Example:

```text
Ocean Agent
     ↓
get_ocean_conditions()
     ↓
Ocean Service
     ↓
PostgreSQL / PostGIS
```

---

# 46. Example PFZ Tool

Conceptual tool:

```python
get_nearest_pfz(
    latitude,
    longitude,
    date,
    radius_km
)
```

Returns structured information:

```text
PFZ ID
Location
Distance
Date
Source
Confidence
```

---

# 47. Example Weather Tool

```python
get_weather_conditions(
    latitude,
    longitude,
    start_time,
    end_time
)
```

Returns:

```text
Wind
Wind gust
Rainfall
Temperature
Pressure
Visibility
Alerts
Timestamp
Source
```

---

# 48. Example Ocean Tool

```python
get_ocean_conditions(
    latitude,
    longitude,
    start_time,
    end_time
)
```

Returns:

```text
SST
Chlorophyll
Wave height
Wave period
Currents
Tides
Timestamp
Source
```

---

# 49. Example Geospatial Tool

```python
check_geofences(
    geometry
)
```

Returns:

```text
Boundary
Distance
Intersection
Restriction
Source
```

---

# 50. Example Hazard Tool

```python
get_marine_hazards(
    geometry,
    start_time,
    end_time
)
```

Returns:

```text
Hazard type
Severity
Location
Valid time
Source
Distance
```

---

# 51. Data Correlation Layer

The correlation layer combines results from multiple tools.

Example:

```text
PFZ Tool
   +
Ocean Tool
   +
Weather Tool
   +
Hazard Tool
   +
Geofence Tool
          ↓
   Correlation Engine
          ↓
      Risk / Zone
       Assessment
```

---

# 52. Correlation Rules

ORCA should use deterministic rules where possible.

Example:

```text
High waves
+
Strong wind
+
Lightning
=
Elevated marine risk
```

The exact risk score should be defined in the risk-engine specification rather than invented by the LLM.

---

# 53. LLM Responsibility

The LLM should primarily handle:

```text
Intent understanding
Planning
Tool selection
Agent coordination
Reasoning over returned evidence
Natural-language explanation
Multilingual interaction
```

The LLM should NOT be responsible for:

```text
Distance calculations
Spatial intersection
Numerical aggregation
Coordinate transformation
Database filtering
Risk arithmetic
```

Those operations belong to deterministic services.

---

# 54. Data Pipeline and Agentic AI

```text
User
 ↓
Orchestrator
 ↓
Planning
 ↓
Tool Selection
 ↓
Data Retrieval
 ↓
Processing
 ↓
Cross-Dataset Correlation
 ↓
Evidence
 ↓
Agent Reasoning
 ↓
Recommendation
```

---

# 55. Pipeline for "Nearest PFZ"

```text
User Query
     ↓
Intent Detection
     ↓
Location Extraction
     ↓
Marine Agent
     ↓
PFZ Tool
     ↓
PostGIS
     ↓
Distance Calculation
     ↓
Nearest PFZ
     ↓
Optional SST/Chlorophyll
     ↓
Marine Analysis
     ↓
Map
     ↓
Answer
```

---

# 56. Pipeline for "Is it Safe Tomorrow?"

```text
User Query
     ↓
Time Resolution
     ↓
Location Resolution
     ↓
Orchestrator
     ↓
┌───────────────┐
│ Weather       │
│ Waves         │
│ Wind          │
│ Lightning     │
│ Cyclone       │
│ Tide          │
│ Advisories    │
└───────────────┘
     ↓
Risk Engine
     ↓
Risk Assessment
     ↓
Evidence Collection
     ↓
Visualization
     ↓
Answer
```

---

# 57. Pipeline for "Why Productivity Declined?"

```text
User Query
      ↓
Historical Analysis Request
      ↓
Retrieve:
   PFZ
   SST
   Chlorophyll
   Ocean Conditions
      ↓
Temporal Alignment
      ↓
Spatial Alignment
      ↓
Trend Analysis
      ↓
Correlation Analysis
      ↓
Evidence
      ↓
Ocean Analytics Agent
      ↓
Explanation
```

The system must distinguish correlation from proven causation.

---

# 58. Pipeline for "Safest Route"

```text
Origin
Destination
   ↓
Geospatial Resolution
   ↓
Generate Candidate Routes
   ↓
Weather Retrieval
   ↓
Wave Retrieval
   ↓
Current Retrieval
   ↓
Hazard Retrieval
   ↓
Geofence Retrieval
   ↓
Constraint Filtering
   ↓
Route Scoring
   ↓
Best Valid Route
   ↓
Map Visualization
   ↓
Explanation
```

---

# 59. Observability

The pipeline should log:

```text
Source requested
Request timestamp
Response status
Records received
Records rejected
Processing time
Database write status
Source freshness
Agent tool invocation
```

Sensitive information must not be unnecessarily logged.

---

# 60. Pipeline Monitoring

The system should expose:

```text
Source availability
Last successful ingestion
Data freshness
Failed ingestion count
Processing failures
API latency
Cache hit rate
```

---

# 61. Data Lineage

ORCA should be able to trace:

```text
User Recommendation
       ↓
Agent Decision
       ↓
Analytical Result
       ↓
Processed Data
       ↓
Raw Data
       ↓
External Source
```

---

# 62. Error Handling

Errors are classified as:

```text
SOURCE_ERROR
NETWORK_ERROR
SCHEMA_ERROR
VALIDATION_ERROR
PROCESSING_ERROR
DATABASE_ERROR
CACHE_ERROR
AGENT_TOOL_ERROR
```

Each should be handled independently.

---

# 63. Data Security

The data pipeline must:

```text
Protect API credentials
Use environment variables
Avoid exposing secrets in logs
Validate external input
Restrict database access
Use service-level permissions
```

---

# 64. Credentials

API keys and secrets must NOT be stored in source code.

Use:

```text
.env
Secret management
Environment variables
```

depending on deployment environment.

---

# 65. Database Transaction Principle

Structured ingestion should use database transactions where appropriate.

```text
Validate
   ↓
Begin Transaction
   ↓
Insert / Update
   ↓
Validate Result
   ↓
Commit
```

If the operation fails:

```text
Rollback
```

---

# 66. Idempotency

Running the same ingestion operation twice should not unnecessarily create duplicate records.

The pipeline should use:

```text
Unique constraints
Upserts
Dataset IDs
Source timestamps
Observation IDs
Checksums
```

where applicable.

---

# 67. Data Retention

Retention policies should distinguish:

```text
Raw datasets
Processed datasets
Historical observations
Temporary cache
Agent execution logs
```

Redis data is temporary.

MinIO can retain raw source files according to storage policy.

---

# 68. Prototype-to-Full-System Principle

The prototype must use the same conceptual pipeline as the final system.

The implementation may initially have fewer sources.

Example:

```text
PROTOTYPE

PFZ
SST
Chlorophyll
Weather
Hazards
Boundaries
   ↓
Same ingestion architecture
   ↓
Same databases
   ↓
Same agent tools
```

Additional datasets can later be connected through the same interfaces.

---

# 69. No Throwaway Architecture

The prototype should NOT use:

```text
Hard-coded responses
Fake AI reasoning
Separate temporary database architecture
Manual JSON pretending to be APIs
LLM-generated numerical values
```

Instead:

```text
Real pipeline
+
Real storage
+
Real tools
+
Real analytical processing
```

The prototype is simply a smaller deployment of the final architecture.

---

# 70. Final Pipeline

```text
                         EXTERNAL SOURCES
                                │
               ┌────────────────┼────────────────┐
               │                │                │
              APIs             FILES          SATELLITE
               │                │                │
               └────────────────┼────────────────┘
                                ▼
                        SOURCE CONNECTORS
                                │
                                ▼
                           INGESTION
                                │
                                ▼
                         RAW MINIO STORAGE
                                │
                                ▼
                           VALIDATION
                                │
                                ▼
                          NORMALIZATION
                                │
                                ▼
                           PROCESSING
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
        PostgreSQL           PostGIS             MinIO
             │                  │                  │
             └──────────────────┼──────────────────┘
                                │
                              Redis
                            (Caching)
                                │
                                ▼
                         SERVICE LAYER
                                │
                                ▼
                           TOOL LAYER
                                │
                                ▼
                         AGENTIC ORCA
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
                 Analysis     Risk       Routing
                    │           │           │
                    └───────────┼───────────┘
                                ▼
                         EVIDENCE LAYER
                                │
                                ▼
                         VISUALIZATION
                                │
                                ▼
                           USER ANSWER
```

---

# 71. Frozen Pipeline Principles

ORCA's data pipeline officially follows these principles:

1. Raw data is preserved where practical.
2. Data is validated before entering trusted storage.
3. Spatial data is handled using PostGIS.
4. Large files are handled using MinIO.
5. Vector knowledge is handled using Qdrant.
6. Redis is used only for temporary/high-speed state and caching.
7. Numerical and spatial reasoning is deterministic.
8. LLMs coordinate and explain rather than fabricate measurements.
9. Every important result should have provenance.
10. Data freshness must be tracked.
11. Source failures must degrade gracefully.
12. The prototype and final system use the same architecture.
13. New data sources must be addable through connectors.
14. Structured retrieval and RAG are complementary, not interchangeable.
15. Recommendations must be evidence-based.
