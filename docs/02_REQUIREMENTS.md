# `02_REQUIREMENTS.md`

# ORCA — System Requirements

**Project Name:** ORCA  
**Document:** System Requirements Specification  
**Document ID:** ORCA-SRS-02  
**Version:** 1.0  
**Status:** FROZEN BASELINE  
**Scope:** Complete ORCA System

---

# 1. Purpose

This document defines the functional and non-functional requirements for ORCA.

It translates the project specification into implementable system requirements.

Each requirement is assigned a unique identifier so that it can later be traced to:

- Architecture
- Agents
- APIs
- Database components
- Frontend components
- Testing
- SIH requirements

---

# 2. Requirement Categories

ORCA requirements are divided into:

- Functional Requirements (FR)
- AI and Agentic Requirements (AI)
- Data Requirements (DR)
- Geospatial Requirements (GEO)
- Safety and Risk Requirements (SAFE)
- RAG and Evidence Requirements (RAG)
- Conversational and Language Requirements (CONV)
- Visualization Requirements (VIS)
- Route Optimization Requirements (ROUTE)
- Security Requirements (SEC)
- Performance Requirements (PERF)
- Reliability Requirements (REL)
- Maintainability Requirements (MAINT)
- Testing and Evaluation Requirements (TEST)

---

# 3. Functional Requirements

## FR-001 — Natural Language Query

The system shall allow users to submit marine-related queries using natural language.

Examples:

- "Where is the nearest PFZ?"
- "Is it safe to go fishing tomorrow?"
- "Show me the safest route."
- "Are there any cyclone alerts near me?"

---

## FR-002 — Query Intent Detection

The system shall identify the intent of a user's query.

Supported intent categories shall include, where applicable:

- PFZ discovery
- Weather inquiry
- Ocean condition inquiry
- Safety assessment
- Hazard inquiry
- Route planning
- Geofencing inquiry
- Fisheries analysis
- Historical analysis
- Marine advisory retrieval
- General marine intelligence

---

## FR-003 — Contextual Query Processing

The system shall process a query using relevant:

- User context
- Geographic context
- Temporal context
- Conversation context
- Previous results

when such information is available.

---

## FR-004 — Multi-Turn Conversation

The system shall support contextual multi-turn conversations.

Example:

User:

> "Find fishing zones near Mumbai."

User:

> "Which one is safest?"

User:

> "What about tomorrow morning?"

ORCA shall understand that subsequent questions refer to the previously established context.

---

## FR-005 — Marine Intelligence Queries

The system shall support conversational marine-intelligence queries involving relevant marine datasets and services.

---

## FR-006 — Evidence-Based Responses

ORCA shall provide evidence supporting important recommendations and factual claims where applicable.

---

## FR-007 — Explainable Recommendations

The system shall explain the major factors contributing to an important recommendation.

---

# 4. Agentic AI Requirements

## AI-001 — Autonomous Planning

ORCA shall autonomously determine the sequence of operations required to answer a complex query.

---

## AI-002 — Task Decomposition

The Orchestrator shall decompose complex user requests into smaller tasks.

Example:

```text
"Is it safe to fish tomorrow morning?"

        ↓

Determine location
        ↓
Retrieve weather
        ↓
Retrieve waves
        ↓
Retrieve wind
        ↓
Retrieve tide
        ↓
Check hazards
        ↓
Check restrictions
        ↓
Assess risk
        ↓
Generate explanation
````

---

## AI-003 — Agent Selection

The system shall select appropriate specialized agents according to the identified task.

---

## AI-004 — Tool Selection

Agents shall be capable of selecting appropriate tools/data sources required to complete their assigned tasks.

---

## AI-005 — Agent Collaboration

Specialized agents shall be capable of exchanging structured results as part of a larger workflow.

---

## AI-006 — Structured Agent Outputs

Agents shall return structured outputs wherever possible rather than relying exclusively on free-form text.

---

## AI-007 — Deterministic Computation

The system shall use deterministic computational components for operations requiring numerical or spatial correctness.

Examples include:

* Distance calculations
* Spatial containment
* Geofencing
* Route calculations
* Numerical transformations
* Data validation

LLMs shall not be treated as the sole source of numerical or geospatial truth.

---

## AI-008 — Result Synthesis

The Orchestrator shall combine outputs from multiple agents into a coherent final response.

---

## AI-009 — Failure Handling

The agentic system shall detect failed or unavailable tools/data sources and handle them without silently presenting fabricated results.

---

# 5. Specialized Agent Requirements

## AI-010 — Orchestrator Agent

The system shall provide an Orchestrator responsible for:

* Intent understanding
* Task planning
* Agent selection
* Tool selection
* Workflow coordination
* Result aggregation
* Final response synthesis

---

## AI-011 — Marine Data Agent

The system shall provide a Marine Data Agent capable of retrieving relevant marine information.

Potential information includes:

* PFZ
* SST
* Chlorophyll
* Waves
* Currents
* Ocean-state information
* Marine advisories

---

## AI-012 — Weather & Hazard Agent

The system shall provide a Weather & Hazard Agent capable of retrieving and interpreting:

* Weather
* Wind
* Rainfall
* Lightning
* Cyclones
* Weather warnings
* Severe-weather information

---

## AI-013 — Ocean Analytics Agent

The system shall provide an Ocean Analytics Agent capable of analyzing relevant oceanographic observations and historical information.

---

## AI-014 — Geospatial Agent

The system shall provide a Geospatial Agent responsible for spatial reasoning and geospatial tool execution.

---

## AI-015 — Risk Assessment Agent

The system shall provide a Risk Assessment Agent capable of evaluating marine operational risk using relevant environmental and spatial factors.

---

## AI-016 — Route Optimization Agent

The system shall provide a Route Optimization Agent capable of generating and evaluating marine routes according to configured constraints.

---

## AI-017 — Evidence / RAG Agent

The system shall provide an Evidence/RAG Agent capable of retrieving supporting knowledge and documents.

---

# 6. Data Requirements

## DR-001 — Multi-Source Data Integration

ORCA shall integrate information from multiple heterogeneous marine, meteorological, fisheries, satellite and geospatial sources.

---

## DR-002 — Potential Fishing Zone Data

The system shall support PFZ information including, where available:

* Location
* Date
* Validity
* Sector
* Associated environmental parameters
* Relevant advisory information

---

## DR-003 — Sea Surface Temperature

The system shall support SST observations and/or forecasts with appropriate:

* Spatial coordinates
* Timestamp
* Value
* Source
* Quality information where available

---

## DR-004 — Chlorophyll-a

The system shall support chlorophyll-a information with appropriate spatial and temporal metadata.

---

## DR-005 — Ocean State

The system shall support relevant ocean-state variables including, where available:

* Wave height
* Wave period
* Swell
* Wind
* Currents
* SST
* Other relevant oceanographic parameters

---

## DR-006 — Weather Data

The system shall support relevant weather information including:

* Forecasts
* Wind
* Rainfall
* Temperature
* Humidity
* Weather warnings

---

## DR-007 — Cyclone Data

The system shall support:

* Cyclone location
* Cyclone track
* Intensity
* Forecast information
* Warning information
* Timestamp

---

## DR-008 — Lightning Data

The system shall support spatially and temporally relevant lightning information where available.

---

## DR-009 — Tide / Sea-Level Data

The system shall support relevant tide and sea-level observations/forecasts where available.

---

## DR-010 — Fisheries Data

The system shall support historical fisheries information such as:

* Fish landings
* Species/resource information
* Fishing effort where available
* Regional information
* Historical records

---

## DR-011 — Vessel / Fishing Activity

Where available and permitted, ORCA shall support vessel/fishing activity information.

---

## DR-012 — Historical Data

ORCA shall support historical marine and fisheries data for temporal analysis.

---

## DR-013 — Data Provenance

Data used for important outputs shall retain metadata identifying the source and relevant timestamp/version where available.

---

## DR-014 — Live Data

The architecture shall support frequently updated data sources without requiring the entire dataset to be permanently downloaded and stored locally.

---

# 7. Geospatial Requirements

## GEO-001 — Geographic Coordinates

The system shall support geographic coordinates for:

* Users
* Vessels
* PFZs
* Hazards
* Routes
* Boundaries
* Other marine features

---

## GEO-002 — Spatial Queries

The system shall support:

* Distance
* Proximity
* Intersection
* Containment
* Buffering
* Spatial filtering

---

## GEO-003 — EEZ

The system shall support Indian maritime/EEZ boundary information.

---

## GEO-004 — Maritime Boundaries

The system shall support relevant maritime boundary layers.

---

## GEO-005 — Marine Protected Areas

The system shall support marine protected-area geometries and associated metadata.

---

## GEO-006 — Restricted Areas

The system shall support configurable restricted operational areas.

---

## GEO-007 — Geofencing

ORCA shall detect when a user/vessel:

* Enters a configured restricted region
* Approaches a restricted region
* Enters a protected area
* Approaches a maritime boundary
* Crosses another configured operational boundary

---

## GEO-008 — Location-Aware Queries

The system shall use geographic context when a query depends on the user's location.

---

## GEO-009 — PFZ Proximity

The system shall be capable of identifying and ranking PFZs according to distance from a specified location.

---

## GEO-010 — Spatial Visualization

Geospatial results shall be visualizable on an interactive map.

---

# 8. Temporal Requirements

## GEO-011 — Timestamp Awareness

Relevant observations shall retain timestamp information.

---

## GEO-012 — Forecast Period Awareness

ORCA shall distinguish current observations from future forecasts.

---

## GEO-013 — Temporal Filtering

The system shall support filtering data according to:

* Date
* Time
* Forecast period
* Advisory validity
* Historical period

---

## GEO-014 — Temporal Correlation

The system shall correlate information from different sources according to appropriate temporal context.

---

# 9. Risk and Safety Requirements

## SAFE-001 — Marine Hazard Detection

The system shall identify relevant marine hazards.

Potential hazards include:

* High waves
* Strong winds
* Lightning
* Cyclones
* Heavy rainfall
* Dangerous currents
* Other configured marine hazards

---

## SAFE-002 — Risk Assessment

ORCA shall evaluate marine operational risk using relevant environmental and geospatial factors.

---

## SAFE-003 — Risk Levels

The system shall support configurable risk categories such as:

* LOW
* MODERATE
* HIGH
* CRITICAL

---

## SAFE-004 — Risk Factors

Risk results shall identify relevant contributing factors.

---

## SAFE-005 — Safety Recommendation

Where sufficient information is available, ORCA shall provide a safety-oriented recommendation.

---

## SAFE-006 — Evidence for Safety Decisions

Important safety recommendations shall include supporting information and source evidence where available.

---

## SAFE-007 — Uncertainty

Where data is unavailable, outdated, incomplete or uncertain, the system shall communicate the limitation rather than presenting false certainty.

---

## SAFE-008 — Proactive Alerts

The system shall support proactive alerts for relevant marine hazards.

---

# 10. Route Optimization Requirements

## ROUTE-001 — Route Generation

The system shall be capable of generating routes between specified marine locations.

---

## ROUTE-002 — Hazard Avoidance

Routes shall be capable of considering configured hazard regions.

---

## ROUTE-003 — Geofence Avoidance

Routes shall be capable of avoiding configured restricted/protected regions.

---

## ROUTE-004 — Marine Condition Awareness

Where data is available, route evaluation shall consider:

* Waves
* Wind
* Currents
* Weather
* Other relevant marine conditions

---

## ROUTE-005 — Route Scoring

Candidate routes shall be evaluated according to configurable criteria.

Potential factors include:

* Distance
* Risk
* Hazards
* Marine conditions
* Restrictions

---

## ROUTE-006 — Route Visualization

Generated routes shall be displayed on the interactive map.

---

## ROUTE-007 — Route Explanation

The system shall explain important factors affecting route selection.

---

# 11. RAG Requirements

## RAG-001 — Knowledge Base

ORCA shall maintain a knowledge base containing relevant marine information.

Potential sources include:

* Marine advisories
* Fisheries information
* Safety guidelines
* Regulations
* Scientific/reference documents

---

## RAG-002 — Document Ingestion

The RAG pipeline shall support ingestion of appropriate document formats.

---

## RAG-003 — Document Processing

Documents shall undergo appropriate:

* Parsing
* Cleaning
* Chunking
* Metadata extraction

---

## RAG-004 — Embedding

Processed documents shall be converted into vector representations for semantic retrieval.

---

## RAG-005 — Vector Search

The system shall support vector similarity search.

---

## RAG-006 — Retrieval

The RAG system shall retrieve relevant information based on the user's query and agent requirements.

---

## RAG-007 — Evidence Association

Retrieved evidence shall remain associated with the generated response where applicable.

---

## RAG-008 — Source Attribution

Where possible, the system shall identify the source document or source metadata used to support an answer.

---

## RAG-009 — RAG and Structured Data Separation

RAG shall not be used as a replacement for authoritative structured marine/weather/geospatial data.

Structured information and knowledge documents shall be handled according to their respective requirements.

---

# 12. Conversational and Multilingual Requirements

## CONV-001 — Language Detection

The system shall automatically identify the language of supported user queries.

---

## CONV-002 — Same-Language Response

ORCA shall respond in the user's detected language where supported.

---

## CONV-003 — Indian Regional Languages

The architecture shall support expansion toward Indian regional languages.

---

## CONV-004 — Context Preservation

Relevant information from previous turns shall be preserved for subsequent queries.

---

## CONV-005 — Context Resolution

The system shall resolve references such as:

* "there"
* "that zone"
* "tomorrow"
* "the safer one"
* "this route"

using available conversation context.

---

# 13. Visualization Requirements

## VIS-001 — Interactive Map

ORCA shall provide an interactive geospatial map.

---

## VIS-002 — PFZ Visualization

PFZ information shall be displayable on the map.

---

## VIS-003 — Hazard Visualization

Relevant hazard regions shall be displayable spatially.

---

## VIS-004 — Route Visualization

Routes shall be displayed on the map.

---

## VIS-005 — Geofence Visualization

Relevant boundaries and geofences shall be displayable.

---

## VIS-006 — Charts

The system shall provide appropriate charts for relevant numerical and historical information.

---

## VIS-007 — Temporal Visualization

Where applicable, users shall be able to understand changes over time.

---

## VIS-008 — Evidence Display

Relevant supporting evidence shall be accessible from the response.

---

## VIS-009 — Alert Interface

Important warnings shall be visually distinguishable from ordinary information.

---

# 14. Database Requirements

## DR-015 — Relational Database

ORCA shall use PostgreSQL for structured application and relational data.

---

## DR-016 — Spatial Database

ORCA shall use PostGIS for spatial storage and geospatial computation.

---

## DR-017 — Cache / Fast State

Redis shall be available for caching and appropriate transient/fast-access state.

---

## DR-018 — Object Storage

MinIO shall be used for large objects such as:

* Documents
* Raster data
* Dataset files
* Other large objects

---

## DR-019 — Vector Storage

Qdrant shall be used for vector storage and semantic retrieval for the RAG system.

---

# 15. Security Requirements

## SEC-001 — Authentication

The system shall provide secure user authentication.

---

## SEC-002 — Authorization

Access to protected resources shall be controlled according to user permissions.

---

## SEC-003 — Secret Management

API keys, credentials and secrets shall not be hardcoded into source code.

---

## SEC-004 — Environment Configuration

Sensitive configuration shall be managed using environment variables or an appropriate secret-management mechanism.

---

## SEC-005 — Input Validation

User and external data shall be validated before processing.

---

## SEC-006 — API Security

Backend APIs shall implement appropriate authentication, validation and rate-control mechanisms.

---

## SEC-007 — Prompt Injection Protection

The agentic and RAG architecture shall include safeguards against malicious instructions contained in user input or retrieved documents.

---

## SEC-008 — Tool Permissions

Agents shall only be allowed to invoke tools appropriate to their responsibilities.

---

# 16. Performance Requirements

## PERF-001 — Responsive Interaction

The conversational interface should provide feedback while long-running operations are executing.

---

## PERF-002 — Parallel Agent Execution

Independent tasks should be capable of executing concurrently where appropriate.

Example:

```text
Weather ───────┐
Ocean ─────────┤
PFZ ───────────┤ → Risk
Geospatial ────┘
```

---

## PERF-003 — Caching

Frequently requested or appropriate data should be cached where possible.

---

## PERF-004 — Efficient Spatial Queries

Spatial queries shall use appropriate spatial indexes and database optimization.

---

## PERF-005 — Large Data Handling

Large datasets shall not unnecessarily be loaded entirely into application memory.

---

# 17. Reliability Requirements

## REL-001 — Source Failure

Failure of an external source shall not cause the entire application to fail unnecessarily.

---

## REL-002 — Partial Results

Where appropriate, ORCA may return partial results while clearly identifying unavailable information.

---

## REL-003 — No Fabricated Data

The system shall not fabricate unavailable weather, ocean, PFZ, hazard or geospatial observations.

---

## REL-004 — Data Freshness

Where data freshness affects the answer, the system shall consider the age of the information.

---

## REL-005 — Provenance

Important results shall retain source/provenance information wherever possible.

---

# 18. Maintainability Requirements

## MAINT-001 — Modular Architecture

ORCA shall use modular components that allow agents, tools and data sources to be added or replaced independently.

---

## MAINT-002 — Agent Independence

Specialized agents should have clearly defined responsibilities and interfaces.

---

## MAINT-003 — Tool Abstraction

External APIs and data sources should be accessed through well-defined tool/service interfaces.

---

## MAINT-004 — Configuration

Thresholds, data-source settings and relevant operational parameters should be configurable rather than hardcoded where appropriate.

---

## MAINT-005 — Logging

Important agent, API, data-ingestion and system events shall be logged.

---

# 19. Testing Requirements

## TEST-001 — Unit Testing

Core functions shall have unit tests.

---

## TEST-002 — API Testing

Backend APIs shall be tested for:

* Valid input
* Invalid input
* Authentication
* Errors
* Expected outputs

---

## TEST-003 — Agent Testing

Agents shall be evaluated for:

* Correct tool selection
* Correct task execution
* Structured output
* Failure handling
* Appropriate reasoning

---

## TEST-004 — RAG Evaluation

RAG shall be evaluated for:

* Retrieval relevance
* Evidence accuracy
* Groundedness
* Retrieval failure

---

## TEST-005 — Geospatial Testing

Geospatial operations shall be tested for:

* Distance
* Containment
* Intersection
* Geofencing
* Route geometry

---

## TEST-006 — Risk Testing

Risk calculations shall be tested against predefined scenarios and expected outcomes.

---

## TEST-007 — Route Testing

Route generation and route scoring shall be evaluated using representative scenarios.

---

## TEST-008 — Multilingual Testing

Supported languages shall be evaluated for:

* Intent detection
* Context preservation
* Response correctness
* Translation/language consistency

---

# 20. SIH Requirement Traceability

The following maps the major SIH expectations to ORCA requirements.

| SIH Capability                    | ORCA Requirement                             |
| --------------------------------- | -------------------------------------------- |
| Natural-language understanding    | FR-001, FR-002                               |
| Automatic language identification | CONV-001                                     |
| Indian regional languages         | CONV-003                                     |
| Multi-turn conversations          | FR-004, CONV-004                             |
| Autonomous planning               | AI-001                                       |
| Task decomposition                | AI-002                                       |
| Tool selection                    | AI-004                                       |
| Agent collaboration               | AI-005                                       |
| Marine data discovery             | AI-011, DR-001                               |
| Weather intelligence              | AI-012, DR-006                               |
| Ocean analytics                   | AI-013                                       |
| Geospatial reasoning              | AI-014, GEO-001–010                          |
| Risk assessment                   | AI-015, SAFE-001–008                         |
| Route optimization                | AI-016, ROUTE-001–007                        |
| RAG/evidence                      | AI-017, RAG-001–009                          |
| Satellite Earth Observation       | DR-003, DR-004 and related marine EO sources |
| PFZ intelligence                  | DR-002, GEO-009                              |
| Safety alerts                     | SAFE-001, SAFE-008                           |
| Geofencing                        | GEO-007                                      |
| Maritime boundaries               | GEO-003, GEO-004                             |
| Protected areas                   | GEO-005                                      |
| Explainable recommendations       | AI-008, FR-007                               |
| Maps                              | VIS-001–005                                  |
| Charts                            | VIS-006–007                                  |
| Evidence                          | FR-006, RAG-007–008                          |
| Multi-source correlation          | DR-001, GEO-014                              |
| Temporal reasoning                | GEO-011–014                                  |

---

# 21. Core Requirement Principle

ORCA shall not be considered successful merely because it can retrieve information from multiple sources.

The system must demonstrate:

```text
UNDERSTAND
    ↓
PLAN
    ↓
SELECT
    ↓
RETRIEVE
    ↓
CORRELATE
    ↓
ANALYZE
    ↓
REASON
    ↓
VALIDATE
    ↓
EXPLAIN
    ↓
RECOMMEND
```

This sequence represents the central functional philosophy of ORCA.

---

# 22. Definition of Requirements Completion

The requirements defined in this document are considered satisfied when the corresponding ORCA implementation can demonstrate that the system:

1. Understands marine queries expressed in natural language.
2. Determines appropriate intent and context.
3. Plans multi-step tasks autonomously.
4. Coordinates specialized agents.
5. Selects and executes appropriate tools.
6. Retrieves heterogeneous marine information.
7. Performs spatial and temporal reasoning.
8. Performs deterministic analytical operations where required.
9. Integrates RAG-based evidence.
10. Performs marine risk assessment.
11. Supports route optimization.
12. Provides geofencing.
13. Generates proactive hazard alerts.
14. Supports multilingual interaction.
15. Maintains multi-turn context.
16. Provides explainable outputs.
17. Presents information through maps and visualizations.
18. Maintains data provenance and appropriate evidence.
19. Handles failures and missing data safely.
20. Provides a modular and maintainable architecture.

---

# 23. Requirement Status

This document defines the baseline requirements for the complete ORCA system.

All subsequent technical documents shall derive their implementation decisions from these requirements.

Changes to major requirements shall be explicitly approved before being incorporated into the project baseline.

````