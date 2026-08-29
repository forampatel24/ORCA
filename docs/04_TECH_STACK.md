# ORCA — Technology Stack

**Project Name:** ORCA  
**Document:** Technology Stack Specification  
**Document ID:** ORCA-TECH-04  
**Version:** 1.0  
**Status:** FROZEN BASELINE  
**Scope:** Complete ORCA System

---

# 1. Technology Philosophy

ORCA will use a production-oriented technology stack rather than a simplified prototype stack.

The stack is selected around the actual requirements of the platform:

- Agentic AI
- Multi-agent orchestration
- RAG
- Geospatial intelligence
- Satellite Earth Observation data
- Marine analytics
- Real-time/near-real-time data
- Route optimization
- Geofencing
- Multilingual interaction
- Explainable recommendations
- Interactive visualization
- Scalable data storage

The system shall avoid using an LLM for tasks that require deterministic numerical or spatial correctness.

---

# 2. Complete Stack

```text
FRONTEND
    React
    TypeScript
    Vite
    Tailwind CSS
    shadcn/ui
    MapLibre GL JS
    ECharts

BACKEND
    Python
    FastAPI
    Pydantic
    SQLAlchemy
    Alembic

AGENTIC AI
    LangGraph
    LangChain
    LLM API
    Tool Calling

RAG
    Qdrant
    Embedding Model/API
    Document Processing
    Reranking

DATABASE
    PostgreSQL
    PostGIS
    Redis
    MinIO

DATA / ANALYTICS
    Python
    Pandas
    NumPy
    GeoPandas
    Shapely
    Xarray
    Rasterio

GEOSPATIAL
    PostGIS
    GeoPandas
    Shapely
    MapLibre
    PROJ

ROUTING
    Routing Engine / Custom Routing
    Graph Algorithms
    Geospatial Constraints

INFRASTRUCTURE
    Docker
    Docker Compose
    Git
    GitHub

TESTING
    Pytest
    HTTPX
    Playwright

MONITORING
    Structured Logging
    Application Metrics
    Error Tracking

CONFIGURATION
    Environment Variables
    .env
````

---

# 3. Programming Languages

## 3.1 Python

Python is the primary backend and intelligence language.

Used for:

* FastAPI
* Agents
* LangGraph
* Data processing
* RAG
* Geospatial processing
* Risk analysis
* Route optimization
* ETL
* API integrations
* Scientific computation

---

## 3.2 TypeScript

TypeScript is the primary frontend language.

Used for:

* React
* UI logic
* Map interaction
* API communication
* State management
* Visualization
* Frontend type safety

---

## 3.3 SQL

SQL is used for:

* PostgreSQL
* PostGIS
* Spatial queries
* Aggregations
* Filtering
* Database optimization

---

# 4. Frontend Stack

## React

React is the primary UI framework.

Responsibilities:

* Chat interface
* Dashboard
* Map interface
* Alerts
* Route visualization
* Data panels
* Evidence panels
* Conversation interface

---

## TypeScript

Used throughout the React application.

Advantages:

* Type safety
* Better API contracts
* Easier maintenance
* Better development experience

---

## Vite

Vite is used as the frontend build tool.

Responsibilities:

* Development server
* Bundling
* Build pipeline
* Fast development environment

---

## Tailwind CSS

Used for application styling.

---

## shadcn/ui

Used for reusable interface components such as:

* Cards
* Dialogs
* Buttons
* Tabs
* Tables
* Dropdowns
* Alerts
* Panels

---

# 5. Mapping Stack

## MapLibre GL JS

MapLibre will be the primary interactive mapping library.

Used for:

* Marine maps
* PFZ visualization
* Vessel location
* Routes
* Hazard zones
* Geofences
* Protected areas
* Maritime boundaries

---

# 6. Visualization Stack

## Apache ECharts

Used for:

* SST charts
* Chlorophyll trends
* Wave conditions
* Weather trends
* Historical fisheries charts
* Risk visualizations
* Time-series plots

---

# 7. Backend Stack

## FastAPI

FastAPI is the primary backend framework.

Responsibilities:

* REST APIs
* Authentication
* Request validation
* Agent workflow APIs
* Data APIs
* Route APIs
* Risk APIs
* Alert APIs

---

## Pydantic

Used for:

* Request schemas
* Response schemas
* Agent state schemas
* Tool input/output validation
* Configuration validation

---

## SQLAlchemy

Used as the primary ORM/database abstraction layer.

Responsibilities:

* Database models
* PostgreSQL interaction
* Transactions
* Query construction

---

## Alembic

Used for database migrations.

Example:

```text
Migration 001
      ↓
Users
      ↓
Migration 002
      ↓
Conversations
      ↓
Migration 003
      ↓
Marine Data
```

---

# 8. Agentic AI Stack

## LangGraph

LangGraph is the primary agent orchestration framework.

Used for:

* Agent workflows
* State management
* Conditional execution
* Parallel execution
* Tool calling
* Multi-agent collaboration
* Workflow recovery

---

## LangChain

LangChain will provide supporting abstractions for:

* LLM interfaces
* Tools
* Prompt management
* Retrieval components
* Structured outputs

LangGraph remains the primary orchestration layer.

---

# 9. LLM Architecture

ORCA will use an LLM through an API rather than requiring a large language model to be downloaded locally.

The LLM is responsible primarily for:

```text
Understanding
Planning
Reasoning
Tool Selection
Agent Coordination
Explanation
Response Generation
```

The LLM should NOT be responsible for authoritative:

```text
Distance calculations
Spatial intersection
Geofence detection
Numerical risk calculations
Route geometry
Database truth
Weather observations
PFZ coordinates
```

Those operations belong to deterministic tools/services.

---

# 10. LLM Provider

The LLM provider shall be API-based.

The architecture shall use an abstraction layer so that the underlying provider/model can be changed without redesigning ORCA.

Conceptually:

```text
ORCA
  │
  ▼
LLM Abstraction
  │
  ├── Provider A
  ├── Provider B
  └── Provider C
```

This prevents vendor lock-in.

---

# 11. Tool Calling

Agents shall use structured tools.

Examples:

```text
get_weather()
get_ocean_conditions()
get_pfz()
get_nearby_pfz()
get_hazards()
check_geofence()
calculate_distance()
analyze_risk()
optimize_route()
search_knowledge()
```

Tools return structured data to the agents.

---

# 12. RAG Stack

The RAG system consists of:

```text
Document
    ↓
Parser
    ↓
Cleaner
    ↓
Chunker
    ↓
Metadata
    ↓
Embedding
    ↓
Qdrant
    ↓
Retriever
    ↓
Reranker
    ↓
Evidence
```

---

# 13. Qdrant

Qdrant is the vector database.

Used for:

* Document embeddings
* Semantic search
* Knowledge retrieval
* Evidence retrieval

---

# 14. Embeddings

The RAG pipeline shall use an embedding model/API appropriate for multilingual marine knowledge.

The embedding layer shall be abstracted so that the embedding provider can be changed without restructuring the RAG system.

---

# 15. Reranking

A reranking layer may be used after initial vector retrieval to improve evidence relevance.

Pipeline:

```text
Query
 ↓
Vector Search
 ↓
Top-K Candidates
 ↓
Reranker
 ↓
Best Evidence
```

---

# 16. Document Processing

Potential libraries:

```text
pypdf
PyMuPDF
python-docx
BeautifulSoup
```

depending on source type.

Documents should be normalized before embedding.

---

# 17. PostgreSQL

PostgreSQL is the primary relational database.

Stores:

```text
Users
Conversations
Messages
Agent Runs
Tool Runs
Alerts
Risk Assessments
Routes
Data Source Metadata
System Configuration
```

---

# 18. PostGIS

PostGIS is the spatial extension of PostgreSQL.

Stores:

```text
PFZ geometries
Vessel locations
Hazards
Geofences
Protected Areas
Maritime Boundaries
Routes
Coastlines
Spatial Metadata
```

Provides:

```text
ST_Distance
ST_Intersects
ST_Contains
ST_Within
ST_Buffer
ST_DWithin
```

and other spatial functions.

---

# 19. Redis

Redis is the high-speed transient data layer.

Used for:

* Caching
* Short-lived state
* Rate limiting
* Background-job support
* Frequently accessed external data
* Temporary workflow information

Redis is NOT the authoritative permanent database.

---

# 20. MinIO

MinIO provides S3-compatible object storage.

Used for:

* PDF files
* Satellite files
* Raster datasets
* Large dataset artifacts
* Uploaded documents
* Intermediate processing files

---

# 21. Data Processing Stack

## Pandas

Used for:

* Tabular data
* Cleaning
* Transformation
* Aggregation
* Historical analysis

---

## NumPy

Used for:

* Numerical operations
* Array processing
* Mathematical calculations

---

## GeoPandas

Used for:

* Vector geospatial data
* Shapefiles
* GeoJSON
* Spatial preprocessing
* GIS transformations

---

## Shapely

Used for geometric operations.

Examples:

* Points
* Lines
* Polygons
* Intersections
* Buffers
* Distance calculations

---

# 22. Earth Observation / Scientific Data

ORCA may work with multidimensional scientific datasets.

Recommended tools include:

## Xarray

Used for:

* NetCDF
* Multidimensional environmental datasets
* Satellite-derived variables
* Time-series ocean data

---

## Rasterio

Used for raster datasets.

Examples:

* Satellite raster products
* GeoTIFF
* Raster environmental layers

---

## PROJ

Used for coordinate reference system and coordinate transformations.

---

# 23. ETL / Data Pipeline

The data pipeline follows:

```text
SOURCE
  ↓
INGEST
  ↓
VALIDATE
  ↓
NORMALIZE
  ↓
TRANSFORM
  ↓
ENRICH
  ↓
STORE
  ↓
INDEX
  ↓
SERVE
```

---

# 24. Data Formats

ORCA shall support appropriate formats including:

```text
JSON
CSV
GeoJSON
Shapefile
GeoTIFF
NetCDF
PDF
Parquet
```

The exact formats depend on the external data source.

---

# 25. Geospatial Stack

The complete geospatial stack is:

```text
PostGIS
GeoPandas
Shapely
PROJ
MapLibre
```

Responsibilities:

| Technology | Purpose                   |
| ---------- | ------------------------- |
| PostGIS    | Spatial database          |
| GeoPandas  | Geospatial preprocessing  |
| Shapely    | Geometry operations       |
| PROJ       | CRS transformations       |
| MapLibre   | Interactive visualization |

---

# 26. Route Optimization

The route engine shall use deterministic algorithms rather than asking the LLM to invent coordinates.

Potential components:

```text
Graph Representation
        ↓
Candidate Route Generation
        ↓
Constraint Filtering
        ↓
Hazard Avoidance
        ↓
Risk Scoring
        ↓
Route Ranking
```

Possible algorithmic approaches include:

* Dijkstra
* A*
* Cost-surface routing
* Graph-based constrained routing

The final implementation shall be selected based on the available marine spatial data.

---

# 27. Risk Engine

Risk assessment should be implemented as a deterministic analytical layer.

Inputs may include:

```text
Wave Height
Wind Speed
Lightning
Cyclone
Rainfall
Current
Tide
Geofence
Other Hazards
```

Output:

```text
Risk Score
Risk Level
Risk Factors
Confidence / Data Quality
```

The LLM then converts this structured result into natural-language reasoning.

---

# 28. API Integration

External APIs should be isolated behind service modules.

Example:

```text
app/
└── services/
    ├── weather/
    ├── ocean/
    ├── pfz/
    ├── cyclone/
    ├── lightning/
    ├── fisheries/
    └── geospatial/
```

This allows individual providers to be replaced without modifying agents.

---

# 29. Caching Architecture

External data that is repeatedly requested may follow:

```text
Agent
  ↓
Data Service
  ↓
Redis Cache
  │
  ├── HIT → Return cached data
  │
  └── MISS
        ↓
     External API
        ↓
      Validate
        ↓
       Redis
        ↓
      Return
```

Cache duration shall depend on data freshness requirements.

---

# 30. Background Processing

Long-running operations should not block normal API requests.

Potential operations include:

* Large data ingestion
* Document processing
* Embedding generation
* Satellite processing
* Bulk data synchronization
* Alert evaluation

Redis-backed job processing may be used where required.

---

# 31. Containerization

Docker shall be used for reproducible infrastructure.

The local architecture will eventually include containerized services such as:

```text
redis
minio
qdrant
```

PostgreSQL/PostGIS may either remain installed directly on the development machine or later be containerized depending on the final deployment architecture.

---

# 32. Docker Compose

Docker Compose shall be used to manage local multi-service infrastructure.

Conceptually:

```text
docker compose up
        │
        ├── Redis
        ├── MinIO
        └── Qdrant
```

Additional services can be added later.

---

# 33. Version Control

## Git

Git is mandatory for source-code version control.

---

## GitHub

GitHub will be used for:

* Repository hosting
* Collaboration
* Branching
* Pull requests
* Issue tracking
* Documentation
* CI/CD

---

# 34. Testing Stack

## Pytest

Used for Python unit and integration testing.

---

## HTTPX

Used for testing FastAPI endpoints.

---

## Playwright

Used for frontend end-to-end testing.

Example:

```text
Open ORCA
    ↓
Enter Query
    ↓
Submit
    ↓
Agent Workflow
    ↓
Map Appears
    ↓
Recommendation Appears
```

---

# 35. Code Quality

Recommended tools:

```text
Ruff
Black
MyPy
Pre-commit
```

Responsibilities:

* Linting
* Formatting
* Type checking
* Automated quality checks

---

# 36. Environment Management

Python dependencies shall be managed using a modern Python environment/package workflow.

The project should maintain:

```text
pyproject.toml
```

rather than manually maintaining an uncontrolled collection of installed packages.

---

# 37. Configuration

Configuration shall be separated from source code.

Example:

```text
.env

DATABASE_URL=...
REDIS_URL=...
MINIO_ENDPOINT=...
QDRANT_URL=...
LLM_API_KEY=...
EMBEDDING_API_KEY=...
```

Secrets shall never be committed to GitHub.

---

# 38. Backend Project Structure

Recommended structure:

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies.py
│   │
│   ├── agents/
│   │   ├── orchestrator/
│   │   ├── marine/
│   │   ├── weather/
│   │   ├── ocean/
│   │   ├── geospatial/
│   │   ├── risk/
│   │   ├── routing/
│   │   └── rag/
│   │
│   ├── tools/
│   │   ├── weather/
│   │   ├── ocean/
│   │   ├── pfz/
│   │   ├── geospatial/
│   │   ├── routing/
│   │   └── database/
│   │
│   ├── services/
│   │   ├── weather/
│   │   ├── ocean/
│   │   ├── fisheries/
│   │   └── external/
│   │
│   ├── models/
│   ├── schemas/
│   ├── database/
│   ├── rag/
│   ├── analytics/
│   ├── geospatial/
│   ├── routing/
│   ├── risk/
│   ├── config/
│   └── utils/
│
├── tests/
│
├── pyproject.toml
├── Dockerfile
└── .env.example
```

---

# 39. Frontend Project Structure

```text
frontend/
│
├── src/
│   ├── components/
│   ├── pages/
│   ├── layouts/
│   ├── maps/
│   ├── charts/
│   ├── chat/
│   ├── alerts/
│   ├── routes/
│   ├── api/
│   ├── hooks/
│   ├── stores/
│   ├── types/
│   └── utils/
│
├── public/
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

# 40. Infrastructure Structure

```text
infra/
│
├── docker/
├── docker-compose.yml
├── postgres/
├── redis/
├── minio/
└── qdrant/
```

---

# 41. Overall Technology Architecture

```text
                         ORCA
                          │
          ┌───────────────┴───────────────┐
          │                               │
       FRONTEND                        BACKEND
          │                               │
 React + TypeScript                    FastAPI
 Vite                                  Python
 Tailwind                              Pydantic
 MapLibre                              SQLAlchemy
 ECharts                               Alembic
          │                               │
          │                         ┌─────┴─────┐
          │                         │           │
          │                    LangGraph     Agents
          │                         │           │
          │                         └─────┬─────┘
          │                               │
          │                            Tools
          │                               │
          │             ┌─────────────────┼─────────────────┐
          │             │                 │                 │
          │           Data             RAG             Analytics
          │             │                 │                 │
          │       PostgreSQL          Qdrant          Pandas
          │       PostGIS             MinIO           NumPy
          │       Redis                              GeoPandas
          │                                          Shapely
          │                                          Xarray
          │                                          Rasterio
          │
          └───────────────────────────────────────────────┐
                                                          │
                                                     Visualization
                                                          │
                                                          ▼
                                                     USER OUTPUT
```

---

# 42. Final Frozen Technology Decisions

| Layer                      | Technology                                  |
| -------------------------- | ------------------------------------------- |
| Frontend                   | React                                       |
| Frontend Language          | TypeScript                                  |
| Build Tool                 | Vite                                        |
| Styling                    | Tailwind CSS                                |
| UI Components              | shadcn/ui                                   |
| Maps                       | MapLibre GL JS                              |
| Charts                     | Apache ECharts                              |
| Backend                    | Python + FastAPI                            |
| Validation                 | Pydantic                                    |
| ORM                        | SQLAlchemy                                  |
| Migrations                 | Alembic                                     |
| Agent Orchestration        | LangGraph                                   |
| Agent Framework Support    | LangChain                                   |
| LLM                        | API-based LLM                               |
| Tool Calling               | Structured tool calling                     |
| Relational DB              | PostgreSQL                                  |
| Spatial DB                 | PostGIS                                     |
| Cache                      | Redis                                       |
| Object Storage             | MinIO                                       |
| Vector DB                  | Qdrant                                      |
| Data Processing            | Pandas                                      |
| Numerical Computing        | NumPy                                       |
| Vector GIS                 | GeoPandas                                   |
| Geometry                   | Shapely                                     |
| Scientific Data            | Xarray                                      |
| Raster Processing          | Rasterio                                    |
| CRS                        | PROJ                                        |
| Routing                    | Graph-based routing                         |
| Testing                    | Pytest                                      |
| API Testing                | HTTPX                                       |
| E2E Testing                | Playwright                                  |
| Linting                    | Ruff                                        |
| Formatting                 | Black                                       |
| Type Checking              | MyPy                                        |
| Version Control            | Git                                         |
| Repository                 | GitHub                                      |
| Containerization           | Docker                                      |
| Multi-container Management | Docker Compose                              |
| Configuration              | Environment Variables                       |
| RAG                        | Qdrant + Embeddings + Retrieval + Reranking |

---

# 43. Technology Selection Principle

No technology exists in ORCA merely because it is popular.

Each component has a specific responsibility:

```text
React
→ User interface

FastAPI
→ Backend/API

LangGraph
→ Agent orchestration

LLM
→ Language + planning + reasoning

PostgreSQL
→ Structured data

PostGIS
→ Spatial intelligence

Redis
→ Fast transient state/cache

MinIO
→ Large objects

Qdrant
→ Semantic/vector retrieval

Pandas/NumPy
→ Data analytics

GeoPandas/Shapely
→ Geospatial processing

Xarray/Rasterio
→ Earth-observation/scientific data

MapLibre
→ Maps

ECharts
→ Visual analytics

Docker
→ Reproducible infrastructure
```

---

# 44. Final Architecture Principle

The most important architectural rule is:

```text
              LLM ≠ DATABASE
              LLM ≠ GIS ENGINE
              LLM ≠ ROUTING ENGINE
              LLM ≠ WEATHER SOURCE
              LLM ≠ RISK CALCULATOR
```

Instead:

```text
LLM
 │
 ├── Understand
 ├── Plan
 ├── Select tools
 ├── Coordinate agents
 ├── Interpret results
 └── Explain
        │
        ▼
Deterministic Systems
 │
 ├── PostgreSQL
 ├── PostGIS
 ├── Redis
 ├── MinIO
 ├── Qdrant
 ├── GIS algorithms
 ├── Risk engine
 ├── Routing engine
 └── External data sources
```

