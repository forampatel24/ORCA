# ORCA — Data Architecture

**Project Name:** ORCA  
**Document:** Data Architecture  
**Document ID:** ORCA-DATA-07  
**Version:** 1.0  
**Status:** FROZEN BASELINE  
**Scope:** Complete Marine, Ocean, Weather, Satellite, Geospatial and Knowledge Data Layer

---

# 1. Purpose

ORCA must combine information from multiple heterogeneous sources.

The system must not depend on a single dataset.

ORCA combines:

- Marine data
- Potential Fishing Zone data
- Oceanographic data
- Satellite Earth Observation data
- Meteorological data
- Wave and sea-state data
- Tide data
- Cyclone and hazard information
- Fisheries information
- Geospatial boundary data
- Marine protected areas
- Maritime boundaries
- Marine advisories
- Scientific and regulatory knowledge

The objective is to transform these heterogeneous sources into a unified intelligence layer.

---

# 2. Core Data Principle

ORCA follows:

```text
RAW DATA
   ↓
INGESTION
   ↓
VALIDATION
   ↓
NORMALIZATION
   ↓
STORAGE
   ↓
INDEXING
   ↓
ANALYTICS
   ↓
AGENT RETRIEVAL
   ↓
CORRELATION
   ↓
INTELLIGENCE
````

---

# 3. Data Categories

ORCA's data architecture is divided into eight major categories.

```text
1. Marine / Fisheries
2. Oceanographic
3. Satellite Earth Observation
4. Meteorological
5. Marine Hazards
6. Geospatial
7. Knowledge / Documents
8. Application / Operational Data
```

---

# 4. Marine / Fisheries Data

This category supports:

* Potential Fishing Zones
* Fish productivity
* Fishing grounds
* Fisheries observations
* Historical fishing information

---

## 4.1 Potential Fishing Zone Data

PFZ data is one of ORCA's primary data sources.

Important attributes may include:

```text
Latitude
Longitude
Date
Time
PFZ geometry
PFZ type
Confidence
Source
Observation period
```

Used by:

```text
Marine Data Agent
Geospatial Agent
Risk Agent
Routing Agent
Visualization Agent
```

---

# 5. Oceanographic Data

Oceanographic data provides information about the physical and biological state of the ocean.

Important variables include:

```text
Sea Surface Temperature
Chlorophyll-a
Wave Height
Wave Period
Wave Direction
Ocean Current
Current Direction
Salinity
Sea Level
```

Not every source will provide every variable.

ORCA's ingestion layer must normalize available variables into a common representation.

---

# 6. Sea Surface Temperature

SST is important for fishing-zone analysis.

ORCA can use SST to:

* Identify thermal patterns
* Compare fishing zones
* Analyze changes over time
* Correlate temperature with PFZ observations
* Support marine productivity reasoning

Used by:

```text
Ocean Analytics Agent
Marine Data Agent
Risk Assessment Agent
Reporting Agent
```

---

# 7. Chlorophyll-a

Chlorophyll concentration is an important ocean biological indicator.

ORCA uses it to:

```text
Analyze marine productivity
Identify productive regions
Correlate with SST
Support PFZ intelligence
Analyze historical changes
```

Used primarily by:

```text
Ocean Analytics Agent
Marine Data Agent
```

---

# 8. Wave Data

Wave information is critical for safety.

Variables may include:

```text
Significant Wave Height
Wave Period
Wave Direction
Swell Height
Swell Direction
```

Used by:

```text
Ocean Agent
Risk Agent
Routing Agent
Alert Agent
```

---

# 9. Ocean Current Data

Current information can support:

* Route optimization
* Marine-condition analysis
* Vessel planning
* Safety analysis

Variables may include:

```text
Current Speed
Current Direction
Latitude
Longitude
Timestamp
Depth
```

---

# 10. Tide Data

Tidal information supports operational planning.

Variables:

```text
Tide Height
High Tide Time
Low Tide Time
Tidal Phase
Location
Prediction Time
```

Used by:

```text
Ocean Agent
Risk Agent
Routing Agent
Reporting Agent
```

---

# 11. Meteorological Data

Weather intelligence is essential to ORCA.

Variables may include:

```text
Temperature
Wind Speed
Wind Direction
Rainfall
Humidity
Pressure
Cloud Cover
Visibility
Lightning
Weather Alerts
```

Used by:

```text
Weather Agent
Risk Agent
Alert Agent
Routing Agent
Reporting Agent
```

---

# 12. Wind Data

Wind is one of the major marine safety variables.

ORCA should preserve:

```text
Wind Speed
Wind Direction
Wind Gust
Timestamp
Forecast Time
Location
```

Wind can be used in:

```text
Risk scoring
Route scoring
Hazard detection
Safety recommendations
```

---

# 13. Lightning Data

Lightning information is used for proactive safety alerts.

Possible attributes:

```text
Latitude
Longitude
Timestamp
Strike intensity
Detection confidence
```

The system can determine whether lightning activity is close to:

```text
Vessel
Fishing zone
Route
User location
Coastal region
```

---

# 14. Cyclone Data

Cyclone information is a high-priority hazard source.

Attributes may include:

```text
Cyclone Name
Center Location
Timestamp
Forecast Time
Wind Speed
Pressure
Category
Forecast Track
Warning Area
```

Used by:

```text
Weather Agent
Risk Agent
Geospatial Agent
Alert Agent
Routing Agent
```

---

# 15. Marine Hazard Data

ORCA must represent different hazard types using a common model.

```text
Hazard
 ├── Type
 ├── Severity
 ├── Location
 ├── Valid From
 ├── Valid To
 └── Source
```

Possible hazards:

```text
Cyclone
Lightning
High Waves
Strong Wind
Heavy Rain
Dangerous Current
Storm
Visibility Hazard
```

---

# 16. Geospatial Data

Geospatial data forms the geographic foundation of ORCA.

Required information includes:

```text
Coastlines
Administrative boundaries
Maritime boundaries
Marine protected areas
Restricted waters
Fishing zones
Ports
Islands
Operational boundaries
Hazard polygons
```

---

# 17. Maritime Boundaries

ORCA must be capable of identifying maritime operational boundaries.

Examples:

```text
Territorial waters
International maritime boundaries
Operational boundaries
Restricted areas
```

These are used by:

```text
Geospatial Agent
Risk Agent
Alert Agent
Routing Agent
```

---

# 18. Marine Protected Areas

Protected-area data supports:

* Geofencing
* Route restriction
* Fishing restriction checks
* Environmental protection

Important fields:

```text
Name
Geometry
Authority
Restriction Type
Effective Period
Description
```

---

# 19. Ports and Coastal Infrastructure

Useful geographic reference information includes:

```text
Ports
Harbours
Fishing harbours
Lighthouses
Coastal settlements
Emergency facilities
```

This can support:

```text
Route planning
Emergency planning
Nearest safe location
Navigation context
```

---

# 20. Bathymetry

Bathymetric data provides ocean depth.

Variables may include:

```text
Latitude
Longitude
Depth
```

Potential uses:

```text
Route planning
Marine context
Navigation
Fishing-zone analysis
```

Bathymetry should be treated as a supporting dataset rather than a real-time hazard source.

---

# 21. Satellite Earth Observation Data

Satellite data is a major component of ORCA.

The architecture should support satellite-derived products rather than assuming one specific satellite mission.

Potential products include:

```text
Sea Surface Temperature
Chlorophyll-a
Ocean Colour
Sea Surface Height
Ocean Surface Conditions
Weather-related observations
```

---

# 22. Raster Data

Many Earth-observation products are raster datasets.

Typical formats include:

```text
GeoTIFF
NetCDF
HDF
Cloud-optimized raster formats
```

Large raster files should be stored in:

```text
MinIO
```

rather than being unnecessarily stored inside PostgreSQL.

---

# 23. Multidimensional Scientific Data

Scientific marine datasets may contain dimensions such as:

```text
Latitude
Longitude
Time
Depth
Variable
```

Example:

```text
SST
 ├── Time
 ├── Latitude
 └── Longitude
```

ORCA's processing layer converts these datasets into queryable analytical representations.

---

# 24. Historical Data

Historical information is required for trend analysis.

Examples:

```text
Historical SST
Historical chlorophyll
Historical wave conditions
Historical weather
Historical PFZ observations
Historical hazards
Historical productivity
```

Historical data enables questions such as:

> "Why has fish productivity declined in this region?"

The system can compare:

```text
Current Conditions
        vs
Historical Conditions
```

---

# 25. Temporal Data Model

ORCA must distinguish between:

```text
Observation Time
Forecast Time
Valid From
Valid To
Ingestion Time
```

Example:

```text
Dataset downloaded:
2026-08-29 10:00

Forecast valid:
2026-08-30 08:00

These are not the same timestamp.
```

---

# 26. Data Freshness

Different data sources require different freshness requirements.

```text
Real-time / near-real-time
        ↓
Weather
Lightning
Vessel position
Marine hazards

Daily / periodic
        ↓
PFZ
Satellite products

Historical
        ↓
Climate / productivity
Long-term marine trends

Static
        ↓
Geofences
Boundaries
Protected areas
```

---

# 27. Data Source Registry

Every external source should be registered in:

```text
data_sources
```

Metadata includes:

```text
Source Name
Provider
Dataset
Endpoint
Format
Update Frequency
Coverage
Variables
Last Successful Update
Status
```

This allows ORCA to know what data is available.

---

# 28. Dataset Metadata

Each dataset should have metadata such as:

```text
Dataset ID
Source
Provider
Variable
Spatial Resolution
Temporal Resolution
Coverage
Coordinate System
Units
Update Frequency
License
Version
```

---

# 29. Data Normalization

Different datasets may use different:

```text
Units
Coordinate systems
Variable names
Timestamp formats
Spatial resolutions
File formats
```

ORCA normalizes them.

Example:

```text
Dataset A:
temperature = Celsius

Dataset B:
temperature = Kelvin

        ↓

Normalization

        ↓

ORCA internal representation:
temperature = Celsius
```

---

# 30. Spatial Normalization

All geographic data must be transformed into compatible spatial representations.

Conceptually:

```text
External CRS
    ↓
CRS Validation
    ↓
Transformation
    ↓
ORCA Spatial Standard
```

The default geographic coordinate system for global latitude/longitude data is:

```text
EPSG:4326
```

where appropriate.

---

# 31. Data Quality Validation

Every ingestion process should validate:

```text
Missing values
Invalid coordinates
Duplicate records
Invalid timestamps
Impossible measurements
Unit mismatches
Schema changes
Corrupt files
```

---

# 32. Quality Flags

Where available, source quality information should be preserved.

Example:

```text
quality_flag
confidence
uncertainty
source_quality
```

ORCA should not discard useful uncertainty information.

---

# 33. Data Provenance

Every important observation should retain:

```text
Source
Dataset
Provider
Observation Time
Ingestion Time
Processing Version
```

This supports explainability.

Example:

```text
Recommendation
     ↓
Based on:
     ├── SST observation
     ├── Chlorophyll observation
     ├── Weather forecast
     └── Marine advisory
```

---

# 34. Data Ingestion Architecture

```text
             EXTERNAL SOURCES
                    │
        ┌───────────┼───────────┐
        │           │           │
     APIs        Files       Satellite
        │           │           │
        └───────────┼───────────┘
                    ▼
              INGESTION LAYER
                    ▼
              VALIDATION
                    ▼
             NORMALIZATION
                    ▼
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
     PostgreSQL   MinIO     Processing
          │                   │
       PostGIS                │
          │                   ▼
          └──────────────► Analytics
```

---

# 35. Data Storage Mapping

```text
Structured Marine Data
        ↓
PostgreSQL

Spatial Marine Data
        ↓
PostGIS

Large Satellite Files
        ↓
MinIO

Scientific Raster/NetCDF
        ↓
MinIO + Processing Layer

Knowledge Documents
        ↓
MinIO

Document Metadata
        ↓
PostgreSQL

Document Embeddings
        ↓
Qdrant

Temporary / Cached Data
        ↓
Redis
```

---

# 36. Data Processing Pipeline

```text
Source
  ↓
Download / API Retrieval
  ↓
Raw Storage
  ↓
Schema Validation
  ↓
Quality Validation
  ↓
Unit Normalization
  ↓
Spatial Normalization
  ↓
Temporal Normalization
  ↓
Transformation
  ↓
Database / Object Storage
  ↓
Indexes
  ↓
Agent Tools
```

---

# 37. Agent-to-Data Mapping

| Agent               | Primary Data                             |
| ------------------- | ---------------------------------------- |
| Orchestrator        | Metadata / agent state                   |
| Marine Agent        | PFZ, fisheries                           |
| Weather Agent       | Weather, wind, rainfall, lightning       |
| Ocean Agent         | SST, chlorophyll, waves, currents, tides |
| Geospatial Agent    | Boundaries, geofences, protected areas   |
| Risk Agent          | All relevant hazard/environmental data   |
| Routing Agent       | Ocean, weather, hazards, geofences       |
| RAG Agent           | Documents, advisories, regulations       |
| Visualization Agent | Analytical outputs                       |
| Reporting Agent     | Evidence from all agents                 |
| Alert Agent         | Real-time/near-real-time hazards         |

---

# 38. Cross-Dataset Correlation

This is one of ORCA's most important capabilities.

The system should correlate:

```text
SST
 +
Chlorophyll
 +
PFZ
 +
Weather
 +
Wave Conditions
 +
Currents
 +
Tides
 +
Hazards
 +
Geofences
```

rather than treating them as independent datasets.

---

# 39. Example Correlation

Question:

> "Which fishing zones are favourable tomorrow?"

ORCA may perform:

```text
PFZ Data
     +
SST
     +
Chlorophyll
     +
Weather Forecast
     +
Wave Conditions
     +
Hazards
     +
Geospatial Restrictions
             ↓
        Zone Analysis
             ↓
      Ranked Fishing Zones
```

---

# 40. Productivity Analysis

Question:

> "Why has fish productivity declined?"

Possible analysis:

```text
Historical PFZ
      +
Historical SST
      +
Historical Chlorophyll
      +
Ocean Conditions
      +
Weather
      +
Other available indicators
          ↓
Temporal Analysis
          ↓
Correlation / Trend Detection
          ↓
Possible Contributing Factors
```

ORCA must distinguish between:

```text
Observed correlation
```

and

```text
Proven causation
```

The system must not claim causation without sufficient evidence.

---

# 41. Safety Analysis

Question:

> "Is it safe to go to sea tomorrow morning?"

ORCA combines:

```text
Weather Forecast
      +
Wind
      +
Wave Height
      +
Wave Period
      +
Lightning
      +
Cyclone
      +
Tide
      +
Marine Advisories
      +
Geospatial Restrictions
          ↓
      Risk Engine
          ↓
Safety Assessment
```

---

# 42. Route Analysis

Question:

> "What is the safest route?"

ORCA combines:

```text
Origin
Destination
      +
Weather
      +
Waves
      +
Currents
      +
Hazards
      +
Geofences
      +
Protected Areas
          ↓
Candidate Routes
          ↓
Constraint Filtering
          ↓
Risk Scoring
          ↓
Recommended Route
```

---

# 43. Data-to-Agent Flow

```text
                DATA SOURCES
                     │
                     ▼
               DATA PLATFORM
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
     Marine       Weather       Ocean
        │            │            │
        └────────────┼────────────┘
                     ▼
               Agent Tools
                     │
                     ▼
              Specialized Agents
                     │
                     ▼
               Risk / Routing
                     │
                     ▼
                Visualization
                     │
                     ▼
                  Reporting
```

---

# 44. Dataset Discovery

ORCA should maintain metadata about available datasets.

The system should be capable of determining:

```text
What data exists?
Where is it?
What variables does it contain?
What time period does it cover?
What geographic area does it cover?
How fresh is it?
Is it suitable for this query?
```

---

# 45. Dynamic Dataset Selection

The Orchestrator should not blindly query every dataset.

Instead:

```text
User Query
    ↓
Intent
    ↓
Required Information
    ↓
Dataset Discovery
    ↓
Relevant Sources
    ↓
Data Retrieval
```

Example:

```text
Query:
"Is it safe tomorrow?"

Required:
Weather
Waves
Wind
Lightning
Cyclone
Advisories

Not necessarily:
Historical SST
```

---

# 46. Data Retrieval Strategy

Data retrieval should follow:

```text
Query
 ↓
Identify location
 ↓
Identify time range
 ↓
Identify required variables
 ↓
Select sources
 ↓
Retrieve data
 ↓
Validate
 ↓
Return structured result
```

---

# 47. Spatial Query Strategy

Spatial queries should be performed using PostGIS whenever practical.

Examples:

```text
Nearest PFZ
Zones within radius
Hazards near route
Route intersecting protected area
Vessel approaching boundary
```

---

# 48. Temporal Query Strategy

Queries should support:

```text
Current
Historical
Forecast
Date range
Time window
```

Example:

```text
Tomorrow morning
=
specific future temporal window
```

The system should resolve natural-language time expressions into explicit timestamps before querying datasets.

---

# 49. Data Caching

Frequently accessed data may be cached using Redis.

Example:

```text
Weather forecast
PFZ result
Marine hazard result
Geofence lookup
```

Cache invalidation must respect data freshness.

---

# 50. Raw vs Processed Data

ORCA should distinguish:

```text
RAW
 ↓
PROCESSED
 ↓
DERIVED
```

Example:

```text
Raw Satellite File
       ↓
Processed SST Raster
       ↓
SST Analytical Layer
       ↓
Agent Result
```

Raw data should be retained where practical for reproducibility.

---

# 51. Derived Data

ORCA may generate derived information such as:

```text
Risk Score
Risk Zones
Route Score
Zone Ranking
Trend
Anomaly
Hazard Proximity
Distance to Boundary
```

Derived results should retain references to the underlying observations used.

---

# 52. Evidence Chain

Every major recommendation should conceptually support:

```text
Recommendation
      ↓
Analysis
      ↓
Derived Metrics
      ↓
Source Observations
      ↓
Original Dataset
```

This creates traceability.

---

# 53. Data Architecture Principle

ORCA is not:

```text
Dataset → LLM → Answer
```

It is:

```text
Multiple Data Sources
        ↓
Data Engineering
        ↓
Structured Storage
        ↓
Spatial / Temporal Analytics
        ↓
Agentic Reasoning
        ↓
Evidence
        ↓
Recommendation
```

---

# 54. Final Data Architecture

```text
                         EXTERNAL DATA
                              │
      ┌───────────────────────┼────────────────────────┐
      │           │           │           │             │
      ▼           ▼           ▼           ▼             ▼
   Marine      Weather     Satellite    Geospatial    Knowledge
      │           │           │           │             │
      └───────────┴───────────┴───────────┴─────────────┘
                              │
                              ▼
                       INGESTION LAYER
                              │
                              ▼
                         VALIDATION
                              │
                              ▼
                        NORMALIZATION
                              │
                 ┌────────────┼────────────┐
                 │            │            │
                 ▼            ▼            ▼
            PostgreSQL      MinIO       Qdrant
                 │
              PostGIS
                 │
                 └────────────┐
                              │
                            Redis
                         (Cache Layer)
                              │
                              ▼
                         AGENT TOOLS
                              │
                              ▼
                    MULTI-AGENT SYSTEM
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
             Analysis       Risk          Routing
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                       Evidence Layer
                              │
                              ▼
                       Visualization
                              │
                              ▼
                          Reporting
                              │
                              ▼
                            USER
```

---

# 55. Frozen Data Categories

ORCA's baseline data architecture officially covers:

```text
✓ Potential Fishing Zones
✓ Fisheries / productivity information
✓ Sea Surface Temperature
✓ Chlorophyll-a
✓ Wave conditions
✓ Ocean currents
✓ Tide information
✓ Weather
✓ Wind
✓ Rainfall
✓ Lightning
✓ Cyclones
✓ Marine hazards
✓ Satellite Earth Observation
✓ Bathymetry
✓ Coastlines
✓ Maritime boundaries
✓ Marine protected areas
✓ Restricted / operational zones
✓ Ports / coastal infrastructure
✓ Marine advisories
✓ Safety information
✓ Regulations
✓ Scientific knowledge
✓ Historical observations
✓ Forecast data
```

The exact external provider/dataset for each variable is handled in the dataset/source registry and can evolve without changing the core architecture.

---

# 56. Final Data Principle

ORCA's intelligence comes from:

```text
DATA DIVERSITY
      +
DATA QUALITY
      +
SPATIAL CONTEXT
      +
TEMPORAL CONTEXT
      +
CROSS-DATASET CORRELATION
      +
AGENTIC REASONING
      +
DETERMINISTIC ANALYTICS
      +
EVIDENCE
```

This is what transforms ORCA from a simple RAG chatbot into a Marine Intelligence Platform.
