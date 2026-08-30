# ORCA — Agentic Marine Intelligence Platform

> An Agentic AI-powered Marine Intelligence Platform that combines satellite Earth Observation, marine, meteorological, geospatial, and advisory data to provide explainable decision support for fishermen and coastal operations.

---

## What is ORCA?

ORCA is an **Agentic AI-powered Marine Intelligence Platform** designed to transform fragmented marine, satellite, weather, oceanographic, and geospatial information into a single intelligent decision-support system.

Instead of simply retrieving information from individual datasets, ORCA:

- understands natural-language queries
- identifies the user's language
- plans the required analysis
- discovers relevant data sources
- retrieves information from multiple heterogeneous datasets
- performs spatial and temporal reasoning
- coordinates specialized AI agents
- evaluates marine risks
- generates explainable recommendations
- presents supporting evidence through maps, charts, alerts, and geospatial visualizations

The goal is to make complex marine intelligence accessible through a simple conversational interface.

---

# The Problem

Fishermen and marine operators often need to make decisions using information distributed across multiple sources.

A single decision may require information about:

- Potential Fishing Zones
- Sea Surface Temperature
- Chlorophyll concentration
- Weather
- Wind
- Waves
- Tides
- Lightning
- Cyclones
- Marine advisories
- Coastal boundaries
- International maritime boundaries
- Restricted waters
- Marine Protected Areas
- Other geospatial constraints

These sources are often heterogeneous and difficult to correlate manually.

For example, answering:

> "Is it safe to go fishing tomorrow morning near this location?"

may require combining:

```text
Weather Forecast
       +
Wave Conditions
       +
Wind
       +
Lightning Risk
       +
Cyclone Information
       +
Tide
       +
Marine Advisories
       +
Geospatial Restrictions
       +
Historical / Contextual Information
       ↓
   Risk Assessment
       ↓
   Recommendation
````

Traditional information systems generally retrieve individual pieces of information.

ORCA aims to **reason across them**.

---

# ORCA's Objective

The primary objective of ORCA is to build an intelligent marine decision-support platform capable of:

1. Understanding natural-language marine queries.
2. Supporting contextual multi-turn conversations.
3. Automatically identifying the user's language.
4. Supporting Indian regional languages.
5. Discovering relevant marine and Earth Observation data.
6. Integrating heterogeneous data sources.
7. Performing spatial reasoning.
8. Performing temporal reasoning.
9. Correlating observations from multiple sources.
10. Assessing marine risks.
11. Providing fishing-zone intelligence.
12. Providing route and navigation assistance.
13. Detecting geospatial restrictions and boundaries.
14. Generating proactive hazard alerts.
15. Providing evidence-backed recommendations.
16. Explaining why a recommendation was generated.

---

# Core Philosophy

ORCA is **not simply a chatbot**.

The fundamental architecture is:

```text
User
 │
 ▼
Natural Language Query
 │
 ▼
Intent Understanding
 │
 ▼
Planner / Orchestrator
 │
 ▼
Agent Selection
 │
 ├──────────────┬──────────────┬──────────────┐
 ▼              ▼              ▼              ▼
Marine Agent   Weather Agent  Ocean Agent   Geo Agent
 │              │              │              │
 └──────────────┴──────────────┴──────────────┘
                       │
                       ▼
                Data & Tools
                       │
                       ▼
             Spatial / Temporal
                  Analysis
                       │
                       ▼
                Risk Analysis
                       │
                       ▼
              Evidence Synthesis
                       │
                       ▼
             Explainable Response
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
             Chat      Map     Charts
```

The LLM is not expected to perform every operation itself.

Deterministic systems perform deterministic work.

For example:

* PostGIS performs spatial queries.
* GeoPandas performs geospatial processing.
* Python performs numerical analysis.
* PostgreSQL stores structured information.
* Qdrant performs vector retrieval.
* Redis handles temporary state and caching.
* MinIO stores large objects.
* Specialized agents coordinate reasoning.

The LLM is primarily used for:

* intent understanding
* planning
* agent coordination
* semantic reasoning
* evidence synthesis
* natural-language explanations

---

# Example User Queries

ORCA is designed to support queries such as:

### Fishing Zone Intelligence

> Where is the nearest Potential Fishing Zone today?

### Marine Safety

> Is it safe to venture into the sea tomorrow morning?

### Marine Conditions

> What are the tide, weather, and sea conditions near my fishing location?

### Hazard Detection

> Are there any lightning or cyclone alerts in my area?

### Ocean Intelligence

> Which regions show high chlorophyll concentration and favourable sea surface temperature?

### Route Planning

> What is the safest route for a fishing vessel considering weather and sea-state conditions?

### Productivity Analysis

> Why has fish productivity declined in this coastal region?

### Geofencing

> Which fishing zones should be avoided because of hazardous conditions or restrictions?

---

# Key Capabilities

## 1. Conversational Marine Intelligence

Users can interact with ORCA using natural language.

The system understands the intent behind the query rather than requiring users to know dataset names or technical parameters.

---

## 2. Multi-Turn Context

ORCA maintains relevant conversational context.

Example:

```text
User:
Is it safe near Mumbai tomorrow?

ORCA:
...

User:
What about around 6 AM?

ORCA:
...
```

The second query can be interpreted using the context established by the first query.

---

## 3. Multilingual Interaction

ORCA is designed to:

* detect the language of the user
* understand supported Indian languages
* generate responses in the user's language

This is particularly important for making marine intelligence accessible to a wider population.

---

# 4. Agentic AI

ORCA uses a modular multi-agent architecture.

Potential specialized agents include:

```text
Planner Agent
Marine Data Agent
Weather Intelligence Agent
Ocean Analytics Agent
Satellite / Earth Observation Agent
Geospatial Reasoning Agent
Risk Assessment Agent
Fishing Zone Intelligence Agent
Route Optimization Agent
Geofence Agent
RAG / Knowledge Agent
Visualization Agent
Reporting Agent
User Interaction Agent
```

Agents are not isolated chatbots.

They collaborate through the ORCA orchestration layer.

---

# 5. Marine Data Integration

ORCA is designed to integrate multiple classes of information:

### Satellite / Earth Observation

Examples include:

* Sea Surface Temperature
* Chlorophyll concentration
* Ocean colour
* Satellite-derived environmental indicators
* Other relevant Earth Observation products

### Meteorological Data

Examples include:

* wind
* rainfall
* temperature
* pressure
* lightning
* cyclone information
* weather forecasts

### Oceanographic Data

Examples include:

* waves
* tides
* sea-state
* currents
* ocean conditions
* other marine observations and forecasts

### Geospatial Data

Examples include:

* coastline
* maritime boundaries
* fishing zones
* restricted areas
* Marine Protected Areas
* ecologically sensitive areas
* operational geofences

### Knowledge Sources

Examples include:

* marine advisories
* official documents
* regulations
* operational guidelines
* historical/contextual documents

---

# 6. Intelligent Data Correlation

ORCA does not treat each dataset independently.

For example:

```text
High Chlorophyll
       +
Suitable SST
       +
Historical Fishing Intelligence
       +
Favourable Ocean Conditions
       ↓
Fishing Suitability Analysis
```

Similarly:

```text
High Waves
       +
Strong Wind
       +
Lightning Risk
       +
Cyclone Warning
       ↓
Marine Risk Assessment
       ↓
Safety Recommendation
```

The system combines evidence before producing its recommendation.

---

# 7. Geospatial Intelligence

Geospatial reasoning is a core component of ORCA.

The system is designed to understand:

* where an event is occurring
* whether a location lies inside a zone
* distance between locations
* intersection between routes and restricted areas
* proximity to hazards
* proximity to fishing zones
* maritime boundaries
* geofences

Spatial operations are performed using deterministic geospatial technologies rather than relying on an LLM to calculate geometry.

---

# 8. Geofencing

ORCA can provide notifications and warnings when a vessel or planned route approaches relevant boundaries.

Potential geofences include:

* International Maritime Boundaries
* Restricted Waters
* Marine Protected Areas
* Ecologically Sensitive Zones
* Fishing Restrictions
* Operational Boundaries
* Other configured geographic constraints

---

# 9. Marine Risk Assessment

ORCA can combine multiple risk factors.

Potential factors include:

```text
Wind
Waves
Lightning
Cyclone
Rainfall
Visibility
Sea State
Tide
Geospatial Restrictions
Marine Advisories
```

These factors can contribute to a structured risk assessment.

The recommendation should always remain connected to its supporting evidence.

---

# 10. Route Optimization

ORCA is designed to support marine route planning.

A route should not simply be:

```text
Shortest distance
```

Instead, route evaluation can consider:

```text
Distance
+
Marine Conditions
+
Weather
+
Hazards
+
Geofences
+
Operational Constraints
```

This enables the system to identify safer and more suitable routes rather than merely geometrically shorter routes.

---

# 11. RAG-Based Marine Knowledge System

ORCA incorporates a Retrieval-Augmented Generation architecture for relevant marine knowledge.

The conceptual pipeline is:

```text
Source Documents
       ↓
Object Storage
       ↓
Document Processing
       ↓
Text Extraction
       ↓
Chunking
       ↓
Embeddings
       ↓
Vector Database
       ↓
Semantic Retrieval
       ↓
Evidence
       ↓
LLM Reasoning
```

RAG is primarily used for knowledge that benefits from semantic retrieval, such as:

* advisories
* regulations
* marine documentation
* operational guidelines
* contextual knowledge
* relevant historical information

---

# 12. Explainable Recommendations

ORCA should not simply return:

> "Do not go fishing."

Instead, the system should be able to explain:

```text
Recommendation:
Avoid the area during the specified period.

Reasons:
• High wave conditions
• Strong winds
• Lightning risk
• Relevant marine advisory

Supporting Evidence:
• Weather source
• Ocean source
• Marine advisory
• Geospatial analysis
```

The objective is to make recommendations **traceable and understandable**.

---

# System Architecture

At a high level:

```text
                    ┌───────────────────┐
                    │       USER        │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  React Frontend   │
                    │ Chat / Map / UI   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   FastAPI API     │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Agent Orchestrator│
                    └─────────┬─────────┘
                              │
          ┌───────────────────┼────────────────────┐
          │                   │                    │
          ▼                   ▼                    ▼
   ┌─────────────┐     ┌─────────────┐      ┌─────────────┐
   │ Marine      │     │ Weather     │      │ Ocean       │
   │ Agent       │     │ Agent       │      │ Agent       │
   └──────┬──────┘     └──────┬──────┘      └──────┬──────┘
          │                   │                    │
          └───────────────────┼────────────────────┘
                              │
             ┌────────────────┼─────────────────┐
             │                │                 │
             ▼                ▼                 ▼
       PostgreSQL/        Qdrant             MinIO
         PostGIS
             │                │                 │
             └────────────────┼─────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Analysis / Risk   │
                    │ / Reasoning       │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Explainable Result│
                    └─────────┬─────────┘
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                  Chat       Map      Charts
```

---

# Technology Stack

## Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* MapLibre GL JS
* Charting/visualization libraries

## Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic
* psycopg

## Databases & Storage

### PostgreSQL

Primary relational database for structured application and analytical data.

### PostGIS

Geospatial extension for PostgreSQL.

Used for:

* spatial queries
* geofencing
* boundaries
* geometry
* spatial relationships
* route analysis

### Qdrant

Vector database used for semantic retrieval and RAG.

### Redis

Used for:

* caching
* temporary state
* rate limiting
* workflow support
* short-lived data

### MinIO

S3-compatible object storage used for large files and datasets.

---

# Geospatial Stack

* PostGIS
* GeoPandas
* Shapely
* PyProj
* Rasterio
* GDAL where required

---

# AI Stack

ORCA uses external LLM APIs rather than requiring a large language model
to be downloaded and hosted locally.

LLMs are used for:

* natural-language understanding
* planning
* reasoning
* agent coordination
* evidence synthesis
* conversational responses

Deterministic computation remains outside the LLM wherever possible.

---

# Infrastructure

Docker Desktop is used to provide reproducible local infrastructure.

The architecture can use containerized services such as:

```text
Redis
Qdrant
MinIO
Prometheus
Grafana
Jaeger
```

PostgreSQL/PostGIS may be provided by the existing local installation during development.

---

# Data Architecture

ORCA separates different classes of data.

```text
                    DATA SOURCES
                         │
                         ▼
                  Data Ingestion
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
          Raw Data              Metadata
              │                     │
              ▼                     ▼
           MinIO                PostgreSQL
              │
              ▼
       Processing Pipeline
              │
              ▼
       Processed / Derived
              │
       ┌──────┴───────┐
       ▼              ▼
  PostgreSQL/       Qdrant
    PostGIS          RAG
```

---

# Storage Responsibilities

| System     | Primary Responsibility                     |
| ---------- | ------------------------------------------ |
| PostgreSQL | Structured application and analytical data |
| PostGIS    | Geospatial data and spatial operations     |
| Qdrant     | Vector embeddings and semantic retrieval   |
| Redis      | Cache and temporary state                  |
| MinIO      | Large files and object storage             |

Each system has a defined responsibility rather than using every database for everything.

---

# Data Processing

The data pipeline follows:

```text
Discover
   ↓
Retrieve
   ↓
Validate
   ↓
Normalize
   ↓
Store Raw Data
   ↓
Process
   ↓
Generate Derived Data
   ↓
Store / Index
   ↓
Expose to Agents
```

The system maintains data provenance wherever practical.

Important metadata can include:

* source
* provider
* dataset
* timestamp
* ingestion time
* geographic coverage
* temporal coverage
* processing information

---

# Project Structure

The repository is organized around clear separation of responsibilities.

```text
ORCA/
│
├── backend/
│
├── frontend/
│
├── agents/
│
├── data/
│
├── infrastructure/
│
├── scripts/
│
├── tests/
│
├── docs/
│   ├── 01_PROJECT_SPEC.md
│   ├── 02_REQUIREMENTS.md
│   ├── 03_ARCHITECTURE.md
│   ├── 04_TECH_STACK.md
│   ├── 05_DATABASE_DESIGN.md
│   ├── 06_AGENT_SPEC.md
│   ├── 07_DATA_ARCHITECTURE.md
│   ├── 08_DATASET_REGISTRY.md
│   ├── 09_DATA_PIPELINE.md
│   ├── 10_RAG_ARCHITECTURE.md
│   ├── 11_AGENT_ORCHESTRATION.md
│   ├── 12_API_SPEC.md
│   ├── 13_FRONTEND_ARCHITECTURE.md
│   ├── 14_SECURITY_ARCHITECTURE.md
│   ├── 15_ML_ANALYTICS_ARCHITECTURE.md
│   ├── 16_DEPLOY_ARCHITECTURE.md
│   ├── 17_TESTING_ARCHITECTURE.md
│   ├── 18_MONITORING_OBSERVABILITY.md
│   ├── 19_DEV_ENVIRONMENT.md
│   └── 20_DATABASE_ARCHITECTURE.md
│
├── AGENTS.md
├── README.md
├── STATUS.md
├── CHANGELOG.md
├── .env.example
└── .gitignore
```

The exact implementation structure may evolve as development progresses.

---

# Development Philosophy

ORCA is being built as the **complete system incrementally**.

The prototype is not a separate throwaway application.

Instead:

```text
Complete Architecture
        ↓
Incremental Implementation
        ↓
Working Milestones
        ↓
Prototype Checkpoint
        ↓
Further Development
        ↓
Complete ORCA
```

Every milestone should therefore produce real components that can remain
part of the final platform.

---

# Development Milestones

Development is divided into milestones.

Each milestone follows:

```text
Plan
 ↓
Implement
 ↓
Test
 ↓
Verify
 ↓
Document
 ↓
Report
 ↓
STOP
```

At the end of every milestone:

* `CHANGELOG.md` is updated
* `STATUS.md` is updated
* `README.md` is updated
* Quick Start is updated if required
* tests are reported
* current implementation status is reported

No automatic Git commit or push is performed.

---

# Current Status

> **M0-M8 Completed — 2026-08-30 (M8 RAG 4 docs 6 chunks Qdrant 6 + M7 GIS Verified)**

Working (all on `D:` `docker_data.vhdx 2.17GB`, not `C:`):
- `docker compose up -d` `orca-*` 30h healthy `9100/6333/6379` + `PostgreSQL 18.4 :5432 PostGIS 3.6.2` + `uvicorn :8000` `GET / 200`
- `M8 RAG 4 docs 6 chunks Qdrant 6 + M7 GIS` `maritime 1 EEZ + protected 2 MPA + geofences 2 + cmfri 8` `ST_Contains true` `ST_DWithin 10km true` `MinIO raster/bathymetry`
- `M5/M6` `POST /chat MODERATE 45` `risk VERY_HIGH` `pfz 0.776` `sst +1.5` `route cost 0.359`

Next: `M5 Specialized Agents + Tools` (Marine/Weather/Ocean/Geo/Risk/Route/RAG specialized agents)

See:

* `STATUS.md` for current implementation state.
* `CHANGELOG.md` for milestone history.
* `AGENTS.md` for development rules.
* `/docs` for detailed architecture specifications.

---

# Quick Start

Verified on Windows 11 + Docker Desktop (data on `D:\Docker\DockerDesktopWSL`):

```bash
# 1. Clone
git clone <repo> && cd ORCA

# 2. Configure (creates backend/.env too)
cp .env.example .env
cp .env.example backend/.env
# set OPENAI_API_KEY in backend/.env for Orchestrator (M4)

# 3. Start infrastructure (all data stays on D:)
docker compose up -d
docker ps  # orca-redis, orca-qdrant, orca-minio healthy

# 4. Verify storage (native PostgreSQL D:\PostreSQL)
$env:PGPASSWORD="postgres"
& "D:\PostreSQL\bin\psql.exe" -U postgres -h localhost -p 5432 -d orca_db -c "SELECT PostGIS_Version(); SELECT count(*) FROM pfz_observations;"
python -c "from minio import Minio; print(Minio('localhost:9100', 'minioadmin','minioadmin', secure=False).list_buckets())"
curl http://localhost:6333/healthz
docker exec orca-redis redis-cli ping  # PONG

# 5. Start Backend API (M3 & M4)
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
# Verify connection to all databases:
# curl http://127.0.0.1:8000/api/v1/health/services

# 6. Frontend (M9 will add full map)
cd frontend && npm install && npm run dev  # http://localhost:5173
```

---

# Security

ORCA must never expose secrets in source code.

Sensitive values must be stored through environment configuration.

Examples include:

* LLM API keys
* database credentials
* MinIO credentials
* external API credentials
* authentication secrets

The repository must never contain real production credentials.

---

# Reliability Principles

ORCA should never fabricate safety-critical information.

If reliable information is unavailable, the system should explicitly state
that the information is unavailable.

The system must distinguish between:

```text
Observed Data
Forecast Data
Derived Data
Retrieved Knowledge
Inference
Recommendation
```

This distinction is important for trustworthy marine intelligence.

---

# Explainability Principles

A recommendation should be traceable to the information used to generate it.

Conceptually:

```text
Recommendation
      ↓
Reasoning Summary
      ↓
Risk Factors
      ↓
Supporting Evidence
      ↓
Source Data
```

The objective is not merely to produce an answer, but to allow the user to
understand **why the answer was produced**.

---

# Future Vision

ORCA is intended to evolve into a comprehensive marine intelligence
platform capable of supporting:

* fishermen
* coastal communities
* marine operators
* navigation planning
* marine safety
* fishing-zone intelligence
* environmental monitoring
* operational decision support

The long-term vision is:

> **Turn complex marine and Earth Observation data into understandable,
> actionable and explainable intelligence.**

---

# License

License information will be added before public release.

---

# Project Status

**Architecture:** Defined (20 docs frozen)
**Documentation:** Defined
**Implementation:** M0-M6 Completed (Foundation + Storage + Pipeline + API + Orchestrator + 8 Agents + Intelligence Engines on D:)
**Prototype:** Not yet reached (M7-M9 pending)
**Production:** Not yet reached

---

## ORCA

**Observe. Reason. Correlate. Act.**

An intelligent marine decision-support platform built around
Agentic AI, geospatial intelligence, Earth Observation data,
and evidence-based reasoning.
