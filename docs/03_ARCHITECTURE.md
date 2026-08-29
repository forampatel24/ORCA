# ORCA — System Architecture

**Project Name:** ORCA  
**Document:** System Architecture Specification  
**Document ID:** ORCA-ARCH-03  
**Version:** 1.0  
**Status:** FROZEN BASELINE  
**Scope:** Complete ORCA System

---

# 1. Architecture Overview

ORCA follows a modular, agentic, service-oriented architecture.

The platform is composed of:

1. Presentation Layer
2. API Layer
3. Agentic Orchestration Layer
4. Specialized Agent Layer
5. Tool / Service Layer
6. Intelligence & Analytics Layer
7. RAG / Knowledge Layer
8. Data Storage Layer
9. External Data Source Layer
10. Monitoring, Security and Infrastructure Layer

The architecture is designed so that:

- Agents do not directly depend on database internals.
- External APIs are accessed through tools/services.
- Deterministic calculations are separated from LLM reasoning.
- Structured data is separated from unstructured knowledge.
- Geospatial computation is handled by geospatial infrastructure.
- RAG is used for knowledge/evidence rather than replacing structured data.
- The Orchestrator coordinates the entire workflow.

---

# 2. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │        USER          │
                         │  Web / Mobile UI     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   PRESENTATION       │
                         │ React + TypeScript   │
                         │ Maps + Charts + Chat  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      API LAYER       │
                         │       FastAPI        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                  ┌────────────────────────────────────┐
                  │       AGENTIC ORCHESTRATOR         │
                  │              LangGraph              │
                  │                                    │
                  │ Intent → Plan → Execute → Validate │
                  └──────────────────┬─────────────────┘
                                     │
             ┌───────────────────────┼───────────────────────┐
             │                       │                       │
             ▼                       ▼                       ▼
      ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
      │ Marine Data │       │   Weather   │       │   Ocean     │
      │    Agent    │       │  & Hazard   │       │  Analytics  │
      └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
             ┌─────────────────────┼─────────────────────┐
             │                     │                     │
             ▼                     ▼                     ▼
      ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
      │ Geospatial │       │    Risk     │       │    Route    │
      │    Agent   │       │   Agent     │       │ Optimization│
      └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │ Evidence / RAG Agent │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Intelligence Engine  │
                         │ Spatial + Temporal + │
                         │ Analytical Reasoning │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Response Synthesis   │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     ▼              ▼              ▼
                  RESPONSE        MAPS           CHARTS
                     │              │              │
                     └──────────────┼──────────────┘
                                    ▼
                                  USER
````

---

# 3. Architectural Layers

## 3.1 Presentation Layer

Responsible for interaction with the user.

### Responsibilities

* Chat interface
* Interactive map
* Charts
* Alerts
* Route visualization
* PFZ visualization
* Geofence visualization
* Evidence display
* Conversation history
* User controls

### Technology

```text
React
TypeScript
Vite
Tailwind CSS
shadcn/ui
MapLibre
ECharts
```

The frontend does not perform authoritative marine calculations.

It communicates with the backend through APIs.

---

# 4. API Layer

The API layer provides the communication boundary between the frontend and backend intelligence system.

### Technology

```text
FastAPI
Pydantic
SQLAlchemy
```

### Responsibilities

* Authentication
* Request validation
* API routing
* Conversation handling
* Agent workflow initiation
* Result delivery
* Error handling
* API security

Example:

```text
POST /api/v1/chat
GET  /api/v1/pfz
GET  /api/v1/weather
GET  /api/v1/ocean
GET  /api/v1/alerts
POST /api/v1/routes/optimize
GET  /api/v1/geofences
POST /api/v1/risk/analyze
```

The API layer should remain separate from the internal agent implementation.

---

# 5. Agentic Orchestration Layer

The Orchestrator is the central control component of ORCA.

### Technology

```text
LangGraph
LLM API
Tool Calling
```

The Orchestrator is responsible for:

* Understanding the request
* Maintaining workflow state
* Creating execution plans
* Selecting agents
* Selecting tools
* Executing tasks
* Managing dependencies
* Handling failures
* Combining results
* Triggering validation
* Producing final response context

---

# 6. Why LangGraph

ORCA requires workflows that are:

* Stateful
* Multi-step
* Conditional
* Parallelizable
* Tool-driven
* Agent-driven
* Recoverable

Therefore, the orchestration layer should represent workflows as a graph.

Conceptually:

```text
                    START
                      │
                      ▼
                Intent Analysis
                      │
                      ▼
                  Planning
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Weather      Ocean        PFZ
          │           │           │
          └───────────┼───────────┘
                      ▼
                Geospatial
                      │
                      ▼
                    Risk
                      │
                      ▼
                 Validation
                      │
                      ▼
                  Evidence
                      │
                      ▼
                  Synthesis
                      │
                      ▼
                    END
```

Independent operations may execute concurrently.

Dependent operations execute after their required inputs become available.

---

# 7. Agent Layer

ORCA contains specialized agents.

```text
1. Orchestrator / Planner Agent
2. Marine Data Agent
3. Weather & Hazard Agent
4. Ocean Analytics Agent
5. Geospatial Agent
6. Risk Assessment Agent
7. Route Optimization Agent
8. Evidence / RAG Agent
```

Each agent has:

* Defined responsibility
* Input schema
* Output schema
* Tool access
* Data dependencies
* Failure behavior

Agents should not have unrestricted access to every system.

---

# 8. Agent Communication

Agents communicate through structured state.

Conceptually:

```text
Agent A
   │
   ▼
Structured Result
   │
   ▼
Shared Workflow State
   │
   ▼
Agent B
```

Example:

```json
{
  "location": {
    "lat": 18.95,
    "lon": 72.82
  },
  "time_window": {
    "start": "...",
    "end": "..."
  },
  "weather": {...},
  "ocean": {...},
  "pfz": [...],
  "geospatial": {...}
}
```

The exact schemas will be defined separately.

---

# 9. Tool Layer

Agents should not directly implement every external integration.

Instead, they access tools.

```text
                    AGENT
                      │
                      ▼
                    TOOL
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       API Tool    DB Tool    Analysis Tool
          │           │           │
          ▼           ▼           ▼
       External     Database   Computation
       Service
```

Tools provide controlled interfaces to:

* External APIs
* PostgreSQL
* PostGIS
* Redis
* MinIO
* Qdrant
* Geospatial calculations
* Routing algorithms
* Data processing
* Analytics

---

# 10. External Data Layer

ORCA consumes information from heterogeneous sources.

Categories include:

### Marine

* PFZ
* SST
* Chlorophyll
* Waves
* Currents
* Ocean observations
* Marine forecasts

### Meteorological

* Weather
* Wind
* Rainfall
* Lightning
* Cyclones
* Warnings

### Fisheries

* Fish landings
* Fisheries observations
* Fishing activity

### Geospatial

* Coastlines
* EEZ
* Maritime boundaries
* Protected areas
* Restricted zones
* Bathymetry

### Knowledge

* Marine advisories
* Regulations
* Safety documents
* Scientific references

---

# 11. Data Ingestion Architecture

External data should enter ORCA through controlled ingestion pipelines.

```text
External Source
      │
      ▼
Source Connector
      │
      ▼
Validation
      │
      ▼
Normalization
      │
      ▼
Transformation
      │
      ├───────────────┐
      ▼               ▼
Structured        Large Object
Data              Storage
      │               │
      ▼               ▼
PostgreSQL/        MinIO
PostGIS
```

For knowledge documents:

```text
Document
   │
   ▼
Parser
   │
   ▼
Cleaner
   │
   ▼
Chunker
   │
   ▼
Metadata
   │
   ▼
Embedding
   │
   ▼
Qdrant
```

---

# 12. Data Storage Architecture

ORCA uses specialized storage systems.

```text
                 ORCA DATA LAYER
                       │
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
 PostgreSQL         PostGIS           Redis
       │               │                │
 Relational        Geospatial       Cache / State
 Data              Data
       │               │
       └───────────────┘

       ┌────────────────────────────────┐
       │                                │
       ▼                                ▼
     MinIO                           Qdrant
 Object Storage                  Vector Storage
```

---

# 13. PostgreSQL

PostgreSQL stores structured relational application information.

Examples:

* Users
* Conversations
* Messages
* Agent execution records
* Data-source metadata
* Alerts
* Risk assessments
* Routes
* Configuration

---

# 14. PostGIS

PostGIS provides spatial storage and computation.

Examples:

* PFZ geometries
* Vessel locations
* Protected areas
* Maritime boundaries
* Geofences
* Routes
* Hazard geometries

Operations include:

* Distance
* Intersection
* Containment
* Buffer
* Proximity
* Spatial filtering

---

# 15. Redis

Redis provides fast-access transient storage.

Potential responsibilities:

* API caching
* External data caching
* Session-related state
* Agent workflow state where appropriate
* Job/queue support
* Rate limiting

Redis should not become the authoritative permanent database.

---

# 16. MinIO

MinIO provides object storage.

Suitable objects include:

* PDF documents
* Dataset files
* Raster files
* Satellite-derived files
* Uploaded documents
* Intermediate data artifacts
* Other large objects

MinIO is not a replacement for PostgreSQL/PostGIS.

---

# 17. Qdrant

Qdrant provides vector storage and semantic retrieval.

It is primarily used by the RAG subsystem.

```text
Document
   ↓
Chunk
   ↓
Embedding
   ↓
Qdrant
   ↓
Semantic Search
   ↓
Relevant Evidence
```

---

# 18. RAG Architecture

The RAG subsystem is independent from structured marine data retrieval.

```text
             USER QUERY
                  │
                  ▼
           Query Processing
                  │
                  ▼
             Embedding
                  │
                  ▼
              Qdrant
                  │
                  ▼
          Relevant Documents
                  │
                  ▼
              Reranking
                  │
                  ▼
              Evidence
                  │
                  ▼
          Agent / Orchestrator
```

RAG is used primarily for:

* Regulations
* Safety guidelines
* Advisories
* Scientific references
* Fisheries knowledge
* Other unstructured marine knowledge

---

# 19. Structured Data vs RAG

ORCA must maintain a strict conceptual separation.

### Structured data

Used for:

* Current SST
* Current weather
* PFZ
* Wave data
* Coordinates
* Boundaries
* Routes
* Historical numerical observations

### RAG

Used for:

* Regulations
* Explanatory documents
* Safety guidance
* Advisories
* Scientific references

Conceptually:

```text
"What is the wave height here?"

        ↓

Structured Data
```

Whereas:

```text
"What safety precautions should fishermen
follow during severe marine weather?"

        ↓

RAG Knowledge
```

Complex queries may use both.

---

# 20. Intelligence Layer

The intelligence layer combines:

* Data retrieval
* Analytics
* Spatial reasoning
* Temporal reasoning
* Risk analysis
* Route analysis
* Evidence

The LLM interprets and coordinates these capabilities.

It should not replace deterministic computational components.

---

# 21. Spatial Reasoning Pipeline

```text
Location
   │
   ▼
Coordinate Normalization
   │
   ▼
PostGIS Query
   │
   ├── PFZ proximity
   ├── Boundary proximity
   ├── Protected area
   ├── Restricted area
   ├── Hazard region
   └── Route intersection
   │
   ▼
Spatial Result
```

---

# 22. Temporal Reasoning Pipeline

```text
User Time Requirement
        │
        ▼
Time Normalization
        │
        ▼
Observation / Forecast Selection
        │
        ▼
Temporal Alignment
        │
        ▼
Cross-Source Comparison
        │
        ▼
Time-Aware Result
```

---

# 23. Spatial + Temporal Reasoning

ORCA's intelligence depends heavily on combining:

```text
WHERE + WHEN + WHAT
```

Example:

```text
User:
"Is it safe near this fishing zone tomorrow morning?"

                 ↓

WHERE
Fishing-zone coordinates

                 +

WHEN
Tomorrow morning

                 +

WHAT
Weather
Wind
Waves
Tide
Lightning
Cyclone
Restrictions

                 ↓

Integrated Analysis
```

---

# 24. Risk Architecture

The Risk Assessment Agent receives validated information from relevant agents.

```text
Weather ────────┐
Waves ──────────┤
Wind ───────────┤
Tide ───────────┤
Lightning ──────┤
Cyclone ────────┤
Currents ───────┤
Geofencing ─────┤
Location ───────┘
        │
        ▼
   Risk Engine
        │
        ▼
Risk Factors
        │
        ▼
Risk Level
        │
        ▼
Recommendation
```

The numerical/scoring component should be deterministic and configurable.

The LLM explains the resulting assessment.

---

# 25. Route Architecture

The Route Optimization Agent receives:

* Origin
* Destination
* Marine conditions
* Hazard information
* Geofences
* Protected areas
* Bathymetry
* Operational constraints

Pipeline:

```text
Origin + Destination
          │
          ▼
   Candidate Routes
          │
          ▼
Restriction Filtering
          │
          ▼
Hazard Analysis
          │
          ▼
Marine Condition Analysis
          │
          ▼
     Route Scoring
          │
          ▼
    Best Candidate
          │
          ▼
       Map Output
```

---

# 26. Response Generation

After all required tasks are complete:

```text
Agent Results
      │
      ▼
Validation
      │
      ▼
Evidence Association
      │
      ▼
Orchestrator
      │
      ▼
Response Generation
      │
      ├──── Text
      ├──── Map
      ├──── Charts
      ├──── Alerts
      └──── Evidence
```

---

# 27. Response Structure

An ORCA response may contain:

```text
ANSWER
   │
   ├── Summary
   │
   ├── Recommendation
   │
   ├── Reasons
   │
   ├── Relevant Data
   │
   ├── Map
   │
   ├── Charts
   │
   ├── Alerts
   │
   └── Evidence
```

---

# 28. Example Query Architecture

## Query

> "Which fishing zone near Mumbai is safest tomorrow morning?"

### Step 1 — Intent

```text
Intent:
PFZ + Safety + Spatial + Temporal
```

### Step 2 — Plan

```text
1. Determine user/reference location
2. Retrieve PFZ
3. Find nearby PFZs
4. Retrieve tomorrow-morning weather
5. Retrieve waves/wind
6. Retrieve hazards
7. Check geofences
8. Assess each PFZ
9. Rank candidates
10. Retrieve supporting evidence
11. Generate response
```

### Step 3 — Parallel Retrieval

```text
PFZ Agent ──────────┐
Weather Agent ──────┤
Ocean Agent ────────┤
Geospatial Agent ───┘
         │
         ▼
      Results
```

### Step 4 — Risk

```text
Results
   ↓
Risk Agent
   ↓
Risk score per PFZ
```

### Step 5 — Synthesis

```text
Risk Results
     +
Evidence
     +
Spatial Information
     ↓
Final Recommendation
```

---

# 29. Parallel Execution

ORCA should execute independent operations in parallel when possible.

For example:

```text
                 Planner
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     Weather      Ocean        PFZ
        │           │           │
        └───────────┼───────────┘
                    ▼
               Geospatial
                    │
                    ▼
                  Risk
```

This reduces unnecessary latency.

---

# 30. Sequential Execution

Some operations depend on previous results.

Example:

```text
User Location
      ↓
Find PFZ
      ↓
Determine PFZ coordinates
      ↓
Retrieve local marine conditions
      ↓
Risk analysis
      ↓
Recommendation
```

The Orchestrator should therefore dynamically manage dependencies.

---

# 31. Event and Alert Architecture

Proactive alerts should operate independently from ordinary chat requests.

```text
Data Update / Event
        │
        ▼
Condition Detection
        │
        ▼
Rule / Risk Engine
        │
        ▼
Alert Trigger
        │
        ▼
User Notification
```

Potential events:

* Cyclone
* Lightning
* High waves
* Dangerous weather
* Geofence proximity
* Restricted-area entry

---

# 32. Geofencing Architecture

```text
Vessel/User Location
        │
        ▼
PostGIS Spatial Query
        │
        ▼
Boundary Comparison
        │
        ├── Safe
        ├── Approaching
        └── Inside
                │
                ▼
              Alert
```

Geospatial decisions are performed using deterministic spatial operations.

---

# 33. Conversation Architecture

Conversation state is managed separately from the LLM itself.

```text
User Message
     │
     ▼
Conversation Manager
     │
     ▼
Context
     │
     ▼
Orchestrator
     │
     ▼
Agent Workflow
     │
     ▼
Response
     │
     ▼
Conversation History
```

Persistent conversation data is stored in PostgreSQL.

Fast temporary state may use Redis.

---

# 34. Language Architecture

```text
User Query
    │
    ▼
Language Detection
    │
    ▼
Intent + Context
    │
    ▼
Language-Independent
Agentic Workflow
    │
    ▼
Response Generation
    │
    ▼
Target Language
    │
    ▼
User
```

The underlying data and computation layer should remain independent of the user's language wherever possible.

---

# 35. Security Architecture

Security controls shall exist across multiple layers.

```text
Frontend
   ↓
Authentication
   ↓
API Security
   ↓
Input Validation
   ↓
Authorization
   ↓
Agent Permissions
   ↓
Tool Permissions
   ↓
Database Security
   ↓
Secrets Management
```

Agents should not receive unrestricted access to all tools.

---

# 36. Error Handling

The architecture shall support graceful failure.

Example:

```text
External API
     │
     X
     │
Source Failure
     │
     ▼
Fallback / Cache
     │
     ├── Available → Continue
     │
     └── Unavailable
              │
              ▼
       Mark Data Missing
              │
              ▼
       Adjust Confidence
              │
              ▼
      Explain Limitation
```

ORCA must not invent unavailable observations.

---

# 37. Observability

The system should record:

* API requests
* Agent execution
* Tool execution
* Data-source failures
* RAG retrieval
* Risk calculations
* Route calculations
* Response generation
* Errors
* Latency

This will allow debugging and evaluation of the agentic workflow.

---

# 38. Deployment Architecture

The eventual deployment environment shall package infrastructure components appropriately.

Conceptually:

```text
                    ORCA
                     │
          ┌──────────┴──────────┐
          │                     │
       Frontend              Backend
          │                     │
          │                  FastAPI
          │                     │
          │                 LangGraph
          │                     │
          │          ┌──────────┼──────────┐
          │          │          │          │
          │        Redis      MinIO     Qdrant
          │
          └───────────────────────────────┐
                                          │
                                   PostgreSQL
                                    + PostGIS
```

Containerization will be used for reproducible infrastructure deployment.

---

# 39. Local Development Architecture

During development on the developer machine:

```text
Host Machine
│
├── Frontend
│
├── Backend
│
└── Docker
     │
     ├── Redis
     ├── MinIO
     └── Qdrant
     
External / Existing
│
└── PostgreSQL + PostGIS
```

The exact deployment arrangement may evolve during implementation without changing the logical architecture.

---

# 40. Architectural Principles

ORCA shall follow these principles.

## Principle 1 — Separation of Concerns

Each component shall have a clearly defined responsibility.

---

## Principle 2 — Deterministic Where Necessary

Critical calculations shall use deterministic algorithms.

---

## Principle 3 — Agentic Where Useful

LLMs should handle:

* Planning
* Interpretation
* Tool selection
* Reasoning
* Explanation

---

## Principle 4 — Evidence First

Important recommendations should be traceable to data or knowledge.

---

## Principle 5 — Data Provenance

The origin and time context of important information should be preserved.

---

## Principle 6 — Modular Agents

Agents should be independently replaceable and extendable.

---

## Principle 7 — Specialized Storage

Each storage technology should be used for the problem it solves best.

---

## Principle 8 — Graceful Failure

Missing data should result in transparent limitations, not fabricated information.

---

## Principle 9 — Spatial and Temporal Awareness

Marine intelligence must consider both location and time.

---

## Principle 10 — Human-Centered Output

Complex computational processes should be translated into understandable decisions and visualizations.

---

# 41. Complete ORCA Architecture

The complete logical architecture can therefore be summarized as:

```text
                             USER
                               │
                               ▼
                    ┌───────────────────┐
                    │   React Frontend  │
                    │ Chat / Map / UI   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │      FastAPI      │
                    │    API Gateway    │
                    └─────────┬─────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   LangGraph Orchestrator │
                 │                         │
                 │ Intent → Plan → Execute │
                 │ → Validate → Synthesize │
                 └────────────┬────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
    Marine Data         Weather & Hazard      Ocean Analytics
       Agent                 Agent                 Agent
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
    Geospatial             Risk Agent         Route Agent
       Agent
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
                     Evidence / RAG Agent
                              │
                     ┌────────┴────────┐
                     │                 │
                     ▼                 ▼
                 Qdrant             MinIO
                 Vectors            Documents
                     │                 │
                     └────────┬────────┘
                              │
                              ▼
                   Spatial / Temporal /
                    Analytical Engine
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        PostgreSQL         PostGIS           Redis
        Relational        Geospatial        Cache/
           Data              Data             State
             │                │                │
             └────────────────┼────────────────┘
                              │
                              ▼
                     External Data Sources
                              │
                              ▼
                  Marine / Weather / EO /
                 Fisheries / Geospatial /
                       Knowledge
                              │
                              ▼
                       ORCA Response
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
                Text         Maps         Charts
                 │            │            │
                 └────────────┼────────────┘
                              ▼
                             USER
```

---

# 42. Architecture Summary

ORCA is fundamentally a layered agentic intelligence system.

The architectural flow is:

```text
USER
 ↓
FRONTEND
 ↓
FASTAPI
 ↓
LANGGRAPH ORCHESTRATOR
 ↓
SPECIALIZED AGENTS
 ↓
TOOLS
 ↓
DATA + COMPUTATION
 ↓
SPATIAL / TEMPORAL REASONING
 ↓
RISK / ROUTE / ANALYTICS
 ↓
RAG + EVIDENCE
 ↓
VALIDATION
 ↓
RESPONSE SYNTHESIS
 ↓
TEXT + MAP + CHART + ALERT
 ↓
USER
```

The architecture deliberately separates:

* Conversation from computation
* Agents from tools
* Structured data from documents
* RAG from live data
* LLM reasoning from deterministic calculations
* Application storage from object storage
* Spatial data from ordinary relational data

This separation is essential to making ORCA scalable, explainable, maintainable and reliable.

