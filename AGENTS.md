# ORCA — AGENTS.md

> This document defines the mandatory development rules, architecture constraints,
> milestone workflow, documentation requirements, and engineering standards for ORCA.

---

# 1. PROJECT IDENTITY

## Project Name

ORCA

## Project Type

Agentic AI-powered Marine Intelligence Platform.

## Primary Objective

ORCA is designed to provide intelligent, evidence-based marine decision support by combining:

- Satellite Earth Observation data
- Marine/oceanographic data
- Meteorological data
- Geospatial data
- Marine advisories
- RAG-based knowledge retrieval
- Specialized AI agents
- Geospatial reasoning
- Risk assessment
- Route optimization
- Conversational AI
- Explainable recommendations

ORCA must not behave like a simple chatbot or a simple dataset-search application.

The system must correlate information from multiple sources and provide
reasoned, evidence-backed marine intelligence.

---

# 2. CORE PRODUCT PRINCIPLE

The system must follow:

    User Query
        ↓
    Intent Understanding
        ↓
    Planning
        ↓
    Agent Selection
        ↓
    Data Discovery
        ↓
    Data Retrieval
        ↓
    Spatial / Temporal Analysis
        ↓
    Cross-Agent Reasoning
        ↓
    Risk Assessment
        ↓
    Recommendation
        ↓
    Evidence
        ↓
    Visualization
        ↓
    User Response

Do not reduce ORCA to:

    User → LLM → Answer

The agentic workflow is a core requirement.

---

# 3. SOURCE OF TRUTH

Before implementing any feature, inspect the documentation in:

    /docs

Important documents include:

    01_PROJECT_SPEC.md
    02_REQUIREMENTS.md
    03_ARCHITECTURE.md
    04_TECH_STACK.md
    05_DATABASE_DESIGN.md
    06_AGENT_SPEC.md
    07_DATA_ARCHITECTURE.md
    08_DATASET_REGISTRY.md
    09_DATA_PIPELINE.md
    10_RAG_ARCHITECTURE.md
    11_AGENT_ORCHESTRATION.md
    12_API_SPEC.md
    13_FRONTEND_ARCHITECTURE.md
    14_SECURITY_ARCHITECTURE.md
    15_ML_ANALYTICS_ARCHITECTURE.md
    16_DEPLOY_ARCHITECTURE.md
    17_TESTING_ARCHITECTURE.md
    18_MONITORING_OBSERVABILITY.md
    19_DEV_ENVIRONMENT.md
    20_DATABASE_ARCHITECTURE.md

These documents define the intended architecture.

Do not casually introduce a different architecture.

If implementation requires a genuine architectural change:

1. Identify the conflict.
2. Explain why the existing architecture is insufficient.
3. Propose the change.
4. Ask before changing a frozen architectural decision.

Do not silently rewrite architecture.

---

# 4. DEVELOPMENT PHILOSOPHY

ORCA is being built as the complete system incrementally.

The prototype is NOT a separate throwaway implementation.

Correct approach:

    Final Architecture
          ↓
    Incremental Implementation
          ↓
    Working Milestones
          ↓
    Prototype Checkpoint
          ↓
    Continued Development
          ↓
    Complete ORCA

Incorrect approach:

    Simplified Prototype
          ↓
    Throw Away
          ↓
    Rebuild Everything

Every milestone should therefore produce code that can remain part of
the final system.

---

# 5. ENGINEERING PRINCIPLE

Always prefer:

    Correct
    Maintainable
    Testable
    Modular
    Secure
    Observable
    Scalable

over:

    Quick
    Hardcoded
    Duplicated
    Temporary
    Fragile

Do not intentionally create technical debt merely to make a milestone
appear complete.

---

# 6. TECHNOLOGY STACK

The current baseline stack is:

## Operating System

Windows 11

## Container Platform

Docker Desktop

## Backend

Python

FastAPI

## Frontend

React

TypeScript

Vite

## Styling

Tailwind CSS / project-approved UI system

## Primary Database

PostgreSQL

## Geospatial Database Extension

PostGIS

## Cache / Temporary State

Redis

## Vector Database

Qdrant

## Object Storage

MinIO

## Geospatial Processing

GeoPandas

Shapely

PyProj

Rasterio

## Database Layer

SQLAlchemy

psycopg

Alembic

## AI

External LLM API

RAG

Multi-Agent Architecture

## Mapping

MapLibre GL JS or the project-approved map library

## Observability

OpenTelemetry

Prometheus

Grafana

Jaeger

## Version Control

Git

GitHub

---

# 7. DATABASE RESPONSIBILITIES

Do not arbitrarily mix storage responsibilities.

## PostgreSQL

Use PostgreSQL for:

- users
- conversations
- messages
- tasks
- agent executions
- dataset metadata
- marine observations
- weather observations
- forecasts
- derived indicators
- risk assessments
- routes
- alerts
- geofence metadata
- audit information
- RAG document metadata

## PostGIS

Use PostGIS for:

- geographic points
- lines
- polygons
- multipolygons
- boundaries
- geofences
- protected areas
- restricted areas
- fishing zones
- spatial relationships
- distance calculations
- intersection queries
- containment queries

## Redis

Use Redis for:

- caching
- temporary state
- short-lived results
- rate limiting
- locks
- appropriate workflow state

Redis is not the authoritative permanent database.

## Qdrant

Use Qdrant for:

- embeddings
- semantic retrieval
- RAG vector search

Do not use Qdrant as the primary relational database.

## MinIO

Use MinIO for:

- satellite files
- raster files
- GeoTIFF
- NetCDF
- CSV/Excel files where appropriate
- PDFs
- raw datasets
- processed files
- generated reports
- other large objects

Do not place large binary files directly into PostgreSQL unless explicitly justified.

---

# 8. DATA PRINCIPLES

Always distinguish:

    Raw Data
    Processed Data
    Derived Data
    Cached Data
    Retrieved Evidence
    Final Recommendation

Do not confuse an observation with an inference.

Do not present a derived value as though it were directly observed.

Do not present stale cached data as fresh data.

Do not fabricate missing information.

---

# 9. DATA PROVENANCE

Whenever practical, preserve:

- source
- provider
- dataset
- timestamp
- ingestion timestamp
- processing information
- spatial coverage
- temporal coverage
- relevant version information

ORCA must be capable of explaining where important information came from.

---

# 10. AGENTIC ARCHITECTURE

Agents are specialized components.

They should not all independently implement the entire ORCA system.

The system should use:

    Orchestrator
        ↓
    Specialized Agents
        ↓
    Tools / Services
        ↓
    Structured Results
        ↓
    Orchestrator
        ↓
    Final Reasoning

Agents should have clearly defined responsibilities.

Avoid unnecessary duplication between agents.

---

# 11. LLM USAGE

LLMs are reasoning/orchestration components.

Do not use an LLM where deterministic computation is more appropriate.

Examples:

Use deterministic code for:

- distance calculations
- coordinate transformations
- geometric intersections
- threshold checks
- numerical calculations
- route geometry operations
- database queries
- data validation

Use LLMs for:

- intent interpretation
- planning
- semantic reasoning
- natural-language explanation
- evidence synthesis
- conversational interaction

---

# 12. NO HARD-CODED INTELLIGENCE

Do not hardcode responses such as:

    "Tomorrow is unsafe."

Instead:

    Data
      ↓
    Analysis
      ↓
    Risk computation
      ↓
    Evidence
      ↓
    Recommendation

The system should derive its result from available information.

---

# 13. EXPLAINABILITY

Important recommendations must be explainable.

The response should be capable of showing:

- what information was used
- which sources contributed
- relevant observations
- relevant forecasts
- relevant geospatial constraints
- risk factors
- reasoning summary
- confidence/uncertainty where applicable

The user should not have to blindly trust an LLM-generated answer.

---

# 14. SAFETY

Marine safety is a critical aspect of ORCA.

Never fabricate:

- weather conditions
- marine conditions
- cyclone warnings
- government advisories
- vessel positions
- boundaries
- risk values
- satellite observations

If reliable information is unavailable:

    State that the information is unavailable.

Do not invent a recommendation.

---

# 15. EXTERNAL DATA

External data sources may change.

Never assume:

- API availability
- API response structure
- dataset freshness
- permanent URLs
- unlimited API quotas

External integrations should be isolated behind services/adapters where possible.

---

# 16. API KEYS AND SECRETS

Never hardcode secrets.

Never commit:

- LLM API keys
- database passwords
- MinIO secrets
- external API keys
- access tokens
- private credentials

Use:

    .env

and maintain:

    .env.example

with placeholder values only.

---

# 17. GIT RULE

Do NOT automatically commit changes.

The developer/user controls commits.

After completing a milestone:

1. Stop.
2. Verify the milestone.
3. Report what was implemented.
4. Report tests performed.
5. Update required documentation.
6. Show the user the current status.
7. Wait for the user's instruction before committing.

Never run:

    git commit

unless explicitly instructed by the user.

Never run:

    git push

unless explicitly instructed by the user.

---

# 18. MILESTONE WORKFLOW

Every milestone must follow this sequence:

    PLAN
      ↓
    IMPLEMENT
      ↓
    TEST
      ↓
    VERIFY
      ↓
    DOCUMENT
      ↓
    STATUS UPDATE
      ↓
    STOP

Do not silently continue into the next major milestone.

---

# 19. MILESTONE COMPLETION REQUIREMENT

A milestone is NOT complete merely because code was written.

It is complete only when:

- implementation exists
- expected functionality works
- relevant tests pass
- errors are addressed
- documentation is updated
- status is updated
- changelog is updated

---

# 20. CHANGELOG.MD

After EVERY completed milestone, update:

    CHANGELOG.md

The changelog should contain:

- milestone number
- milestone name
- date
- major changes
- new components
- important fixes
- tests
- architectural decisions if applicable

Example:

    ## Milestone 01 — Project Foundation

    Date: YYYY-MM-DD

    Added:
    - FastAPI backend
    - React frontend
    - Docker infrastructure

    Tests:
    - Backend health check
    - Frontend startup
    - Database connectivity

Do not rewrite historical entries unnecessarily.

Add a new entry.

---

# 21. STATUS.MD

After EVERY completed milestone, update:

    STATUS.md

STATUS.md must always represent the current state of the project.

It should contain:

- current milestone
- completed milestones
- current implementation state
- working components
- pending components
- known issues
- next milestone
- current architecture status

Do not leave STATUS.md describing an outdated project state.

---

# 22. README.MD

After EVERY completed milestone, update the relevant README sections.

At minimum, keep these sections current:

    ## What is ORCA?
    ## Current Status
    ## Quick Start

The README should accurately reflect what currently works.

Do not claim features that have not been implemented.

---

# 23. README — WHAT IS ORCA?

The "What is ORCA?" section should remain a concise explanation of:

- ORCA's purpose
- the marine intelligence problem
- the agentic architecture
- the major capabilities

This section should evolve only when the actual product scope changes.

---

# 24. README — CURRENT STATUS

The current status should state:

- current milestone
- working functionality
- major implemented components
- major remaining work

Avoid vague statements such as:

    "Project almost complete."

Use measurable statements instead.

---

# 25. README — QUICK START

After each milestone, ensure the Quick Start section reflects the actual
commands required to run the current implementation.

For example:

    1. Clone repository
    2. Configure environment
    3. Start infrastructure
    4. Start backend
    5. Start frontend
    6. Open application

Only document commands that actually work.

---

# 26. MILESTONE REPORT TO USER

After every milestone, provide the user with a concise report containing:

## What I Built

List the implemented components.

## What the Project Is

Explain what ORCA currently does in simple terms.

## What Changed

Describe the important changes from the previous milestone.

## Tests

List tests/checks performed and their results.

## Current Status

State what works now.

## Remaining

State what is not implemented yet.

## Next Milestone

State exactly what should be built next.

---

# 27. DO NOT CLAIM SUCCESS WITHOUT TESTING

Never say:

    "Everything works."

unless the relevant functionality was actually tested.

Use precise statements:

    "Backend starts successfully."

    "PostgreSQL connection verified."

    "Redis connectivity verified."

    "Frontend renders successfully."

---

# 28. ERROR HANDLING

Errors should be:

- explicit
- logged
- actionable
- structured where appropriate

Do not silently swallow exceptions.

Avoid:

    except:
        pass

unless there is an extremely specific and documented reason.

---

# 29. LOGGING

Important backend operations should produce structured logs.

Examples:

- request received
- task created
- agent started
- tool called
- data source queried
- retrieval performed
- risk calculation completed
- recommendation generated
- error occurred

Do not log secrets.

---

# 30. OBSERVABILITY

ORCA should eventually provide visibility into:

- API latency
- agent execution
- tool execution
- errors
- database performance
- external API failures
- RAG retrieval
- task execution

Observability should be added incrementally according to the architecture.

---

# 31. CODE ORGANIZATION

Prefer modular architecture.

Avoid creating one enormous:

    main.py

containing:

- APIs
- database logic
- agents
- prompts
- business logic
- external integrations
- data processing

Separate responsibilities into appropriate modules.

---

# 32. SEPARATION OF CONCERNS

Prefer:

    API
      ↓
    Service
      ↓
    Repository
      ↓
    Database

and:

    Agent
      ↓
    Tool
      ↓
    External Service

where appropriate.

---

# 33. DATABASE ACCESS

Do not scatter raw database queries throughout the frontend or agent code.

Database access belongs in backend database/service layers.

---

# 34. FRONTEND PRINCIPLES

The frontend should not contain business-critical decision logic.

Frontend responsibilities:

- presentation
- interaction
- visualization
- user input
- map interaction
- displaying results

Backend responsibilities:

- data retrieval
- calculations
- agents
- reasoning
- validation
- security
- persistence

---

# 35. TYPESCRIPT

Avoid unnecessary:

    any

Prefer strongly typed interfaces and API models.

Backend and frontend contracts should remain synchronized.

---

# 36. API CONTRACTS

API request/response structures should be defined clearly.

When API contracts change:

1. Update backend schema.
2. Update frontend types.
3. Update API documentation.
4. Test both sides.

---

# 37. PYTHON QUALITY

Prefer:

- type hints
- clear function names
- small functions
- modular classes where appropriate
- validation
- docstrings for important public interfaces

Avoid unnecessarily complicated abstractions.

---

# 38. FRONTEND QUALITY

Prefer:

- reusable components
- clear state management
- typed API responses
- reusable map components
- reusable visualization components
- accessible UI

Avoid putting all UI logic into a single component.

---

# 39. DATA PIPELINES

Data ingestion should follow:

    Discover
       ↓
    Retrieve
       ↓
    Validate
       ↓
    Normalize
       ↓
    Store Raw
       ↓
    Process
       ↓
    Store Processed
       ↓
    Index / Catalog
       ↓
    Make Available to Agents

Do not directly mix ingestion, transformation, analysis and presentation.

---

# 40. RAW DATA PRESERVATION

Where practical, preserve raw source data.

This allows:

- reproducibility
- debugging
- reprocessing
- provenance
- comparison after pipeline changes

---

# 41. RAG PIPELINE

The RAG pipeline should follow:

    Source Document
         ↓
    MinIO
         ↓
    Text Extraction
         ↓
    Cleaning
         ↓
    Chunking
         ↓
    Embeddings
         ↓
    Qdrant
         ↓
    Retrieval
         ↓
    Evidence
         ↓
    LLM Reasoning

Metadata should remain linked to the source document.

---

# 42. RAG SAFETY

Retrieved information must not automatically be treated as current truth.

Check:

- source
- date
- relevance
- geographic applicability
- temporal applicability

when applicable.

---

# 43. GEOSPATIAL PRINCIPLES

Coordinate reference systems must be handled explicitly.

Do not assume all geographic data uses the same CRS.

Before spatial calculations:

1. Identify CRS.
2. Transform if required.
3. Perform the calculation.
4. Preserve appropriate CRS information.

---

# 44. SPATIAL OPERATIONS

Use deterministic geospatial libraries for:

- distance
- intersection
- containment
- buffering
- spatial joins
- geometry validation

Do not ask an LLM to calculate geometry.

---

# 45. TEMPORAL REASONING

Marine intelligence is time-sensitive.

Always distinguish:

- observation time
- forecast generation time
- forecast target time
- ingestion time
- current time

Never treat all timestamps as interchangeable.

---

# 46. FRESHNESS

When using time-sensitive information, determine whether the information is:

    Current
    Recent
    Forecast
    Historical
    Stale
    Unavailable

Do not silently use stale information for safety-critical recommendations.

---

# 47. ROUTING

Routing should combine:

- geographic constraints
- marine conditions
- weather
- hazards
- geofences
- operational constraints

A route should not simply be the shortest geometric path.

---

# 48. RISK

Risk assessment should be evidence-driven.

Potential factors include:

- wind
- waves
- lightning
- cyclone conditions
- visibility
- rainfall
- geofencing restrictions
- other relevant marine hazards

Risk calculations should remain transparent.

---

# 49. MULTI-LANGUAGE SUPPORT

ORCA should support:

- language identification
- multilingual responses
- Indian regional languages

The system should respond in the user's language where supported.

Do not hardcode language-specific responses unnecessarily.

---

# 50. CONVERSATIONAL CONTEXT

ORCA must support multi-turn interactions.

Example:

    User:
    Is it safe near Mumbai tomorrow?

    User:
    What about at 6 AM?

The second query should be interpreted in context.

Do not unnecessarily ask the user to repeat known information.

---

# 51. AGENT MEMORY

Do not store arbitrary conversational information permanently.

Distinguish:

- conversation context
- task state
- persistent user information
- temporary agent state

Use the appropriate storage mechanism.

---

# 52. PERFORMANCE

Do not optimize prematurely.

First ensure:

    Correctness
       ↓
    Reliability
       ↓
    Testability
       ↓
    Performance Optimization

When performance problems appear, measure before optimizing.

---

# 53. SECURITY

Follow secure defaults.

Important principles:

- validate inputs
- authenticate protected endpoints
- authorize access
- protect secrets
- sanitize file inputs
- restrict CORS
- avoid arbitrary command execution
- avoid unsafe deserialization
- validate uploaded datasets

---

# 54. FILE UPLOADS

Uploaded files must be:

- validated
- size-limited
- type-checked
- safely stored
- scanned/validated as appropriate

Never blindly trust file extensions.

---

# 55. DEPENDENCIES

Do not install random packages without justification.

Before adding a dependency, consider:

- Does the project actually need it?
- Is it maintained?
- Does an existing dependency already solve the problem?
- Does it introduce security or licensing concerns?
- Does it conflict with the architecture?

---

# 56. DOCKER

Docker is used to provide reproducible infrastructure.

Do not install multiple copies of infrastructure unnecessarily.

Current architecture:

    PostgreSQL + PostGIS
        → existing local installation

    Docker:
        Redis
        Qdrant
        MinIO
        Prometheus
        Grafana
        Jaeger

If architecture changes, document why.

---

# 57. DOCKER DATA

Docker Desktop application installation and Docker data storage are separate concerns.

Large Docker data should preferably be located on the designated project/data drive.

Do not casually delete Docker volumes.

Deleting volumes may destroy project data.

---

# 58. LOCAL DEVELOPMENT

The project should be runnable locally without requiring production infrastructure.

Local services should use:

    localhost

where appropriate.

---

# 59. TESTING REQUIREMENT

Every major feature should have appropriate tests.

Testing levels include:

    Unit Tests
    Integration Tests
    API Tests
    Agent Tests
    RAG Tests
    Geospatial Tests
    End-to-End Tests

Not every tiny function requires an end-to-end test.

Use the appropriate testing level.

---

# 60. TESTING AFTER MILESTONES

Before declaring a milestone complete:

    Run relevant tests
        ↓
    Inspect failures
        ↓
    Fix failures
        ↓
    Run again
        ↓
    Document results

---

# 61. NO PROTOTYPE-ONLY HACKS

Avoid:

- fake APIs
- fake agent outputs
- hardcoded risk scores
- hardcoded weather
- fake geospatial results
- fake RAG responses

unless explicitly required for a clearly isolated test.

If mocks are required, clearly label them as mocks.

---

# 62. CONFIGURATION

Configuration should be centralized.

Avoid scattering:

    localhost:8000

or:

    API URLs

throughout the codebase.

Use environment/configuration management.

---

# 63. NAMING

Use clear names.

Prefer:

    MarineDataService

over:

    MDS

Prefer:

    RiskAssessmentService

over:

    RAS

unless an abbreviation is already an established project convention.

---

# 64. COMMENTS

Comments should explain:

    WHY

rather than simply:

    WHAT

Avoid comments that merely restate obvious code.

---

# 65. DOCUMENTATION

When implementation changes architecture or behavior, update the relevant
documentation.

Do not allow code and documentation to drift apart.

---

# 66. NO SILENT ARCHITECTURAL CHANGES

If an implementation cannot follow the documented architecture:

STOP.

Explain:

1. What conflicts.
2. Why it conflicts.
3. What alternatives exist.
4. What change is proposed.

Wait for approval before changing a frozen architecture.

---

# 67. MILESTONE BOUNDARIES

At the end of each major milestone:

STOP DEVELOPMENT.

Do not automatically start the next milestone.

The user must decide when to continue.

---

# 68. MILESTONE CHECKLIST

Before reporting completion:

[ ] Feature implemented

[ ] Relevant architecture respected

[ ] Tests written/updated

[ ] Tests executed

[ ] Errors fixed

[ ] No secrets committed

[ ] CHANGELOG.md updated

[ ] STATUS.md updated

[ ] README.md updated

[ ] Quick Start updated

[ ] Current project status verified

[ ] No git commit performed

[ ] No git push performed

---

# 69. USER REPORT FORMAT

After each milestone, report:

    # Milestone X Complete

    ## What I Built

    ...

    ## What ORCA Is Now

    ...

    ## Files Added/Changed

    ...

    ## Tests

    ...

    ## Current Status

    ...

    ## Known Issues

    ...

    ## Next Milestone

    ...

Then STOP.

---

# 70. CHANGELOG FORMAT

Use:

    ## Milestone X — Name

    Date: YYYY-MM-DD

    ### Added
    - ...

    ### Changed
    - ...

    ### Fixed
    - ...

    ### Tests
    - ...

    ### Notes
    - ...

---

# 71. STATUS FORMAT

STATUS.md should contain:

    # ORCA — Current Status

    ## Current Milestone

    ...

    ## Completed

    ...

    ## Working

    ...

    ## In Progress

    ...

    ## Pending

    ...

    ## Known Issues

    ...

    ## Next Milestone

    ...

    ## Architecture Status

    ...

---

# 72. README QUICK START

README Quick Start must always match the current implementation.

Never document a command that has not been verified.

If setup differs between Windows and production, clearly distinguish them.

---

# 73. PROJECT DIRECTORY

Maintain a clean structure.

Conceptually:

    ORCA/
    │
    ├── backend/
    ├── frontend/
    ├── agents/
    ├── data/
    ├── infrastructure/
    ├── scripts/
    ├── tests/
    ├── docs/
    │
    ├── README.md
    ├── AGENTS.md
    ├── STATUS.md
    ├── CHANGELOG.md
    ├── .env.example
    └── .gitignore

The exact structure may evolve according to the architecture.

---

# 74. GITIGNORE

The repository must ignore:

- .env
- virtual environments
- node_modules
- Python caches
- generated files
- local databases where applicable
- secrets
- large temporary datasets
- Docker local artifacts where appropriate

---

# 75. NO UNNECESSARY DATA DUPLICATION

Do not store the same large dataset in:

- PostgreSQL
- MinIO
- local filesystem
- Git

without a specific reason.

Define the authoritative location.

---

# 76. SOURCE OF TRUTH FOR DATA

For every major data type, there should be a clear source of truth.

Examples:

    Structured application state
        → PostgreSQL

    Geospatial relational state
        → PostgreSQL/PostGIS

    Vector embeddings
        → Qdrant

    Large objects
        → MinIO

    Temporary/cache state
        → Redis

---

# 77. DEVELOPMENT VS PRODUCTION

Local development configuration must not be assumed to be production-ready.

However, local architecture should remain conceptually compatible with the
intended production architecture.

---

# 78. NO UNNECESSARY REWRITES

Do not rewrite working modules simply because a different implementation
looks cleaner.

Prefer incremental improvement.

---

# 79. REFACTORING

Refactor when:

- duplication becomes significant
- responsibilities are mixed
- tests become difficult
- architecture is being violated
- maintainability is significantly reduced

Avoid refactoring purely for cosmetic reasons during a milestone.

---

# 80. FAILURE PRINCIPLE

When something fails:

    Reproduce
        ↓
    Identify root cause
        ↓
    Fix root cause
        ↓
    Test
        ↓
    Document if significant

Do not repeatedly patch symptoms without understanding the cause.

---

# 81. EXTERNAL API FAILURE

External services may fail.

ORCA should handle:

- timeout
- rate limit
- malformed response
- unavailable service
- authentication failure
- stale response

with explicit error states.

---

# 82. LLM FAILURE

The system must handle:

- API failure
- quota exhaustion
- timeout
- malformed output
- invalid structured output

LLM failure must not silently become fabricated information.

---

# 83. STRUCTURED LLM OUTPUT

Where an agent requires structured information from an LLM, validate the
output against a defined schema.

Do not blindly trust arbitrary generated JSON.

---

# 84. AGENT LOOP SAFETY

Agents must not be allowed to execute uncontrolled infinite loops.

Agent workflows should have:

- step limits
- timeout limits
- retry limits
- failure handling

---

# 85. TOOL ACCESS

Agents should only receive tools relevant to their responsibilities.

Do not give every agent unrestricted access to every system.

---

# 86. DATABASE SAFETY

Agents should not directly perform arbitrary destructive database operations.

Use controlled service interfaces.

---

# 87. USER EXPERIENCE

ORCA should prioritize:

- clarity
- trust
- explainability
- simplicity
- actionable information

A technically sophisticated backend should not result in a confusing UI.

---

# 88. MAP EXPERIENCE

Maps are a core part of ORCA.

Where relevant, map outputs should communicate:

- location
- marine conditions
- hazards
- geofences
- routes
- fishing zones
- relevant spatial evidence

---

# 89. VISUALIZATION

Charts should answer a question.

Do not add charts merely to make the interface look sophisticated.

Examples:

    How is wave height changing?

    What is the SST trend?

    Which area has higher fishing suitability?

---

# 90. EVIDENCE PRESENTATION

When ORCA provides a recommendation, evidence should be accessible.

Example:

    Recommendation
        ↓
    Why?
        ↓
    Evidence
        ├── Weather
        ├── Ocean
        ├── Satellite
        └── Geospatial

---

# 91. CURRENT DEVELOPMENT RULE

At the beginning of every milestone:

1. Inspect current repository.
2. Read relevant documentation.
3. Read STATUS.md.
4. Identify the exact milestone objective.
5. Plan the implementation.
6. Implement only what belongs to the milestone.

Do not assume the repository is in the state you expect.

---

# 92. BEFORE MODIFYING CODE

Inspect existing:

* files
* dependencies
* configuration
* database schema
* API contracts
* tests

Avoid overwriting existing work blindly.

---

# 93. AFTER MODIFYING CODE

Check:

* imports
* syntax
* type errors where applicable
* configuration
* database connectivity
* API behavior
* frontend build
* relevant tests

---

# 94. NEVER HIDE FAILURES

If something remains broken at the end of a milestone:

Report it.

Use:

```
Known Issue:
...
```

Do not mark the milestone fully successful if a critical component is broken.

---

# 95. MILESTONE DOCUMENTATION IS MANDATORY

Every completed milestone MUST update:

```
CHANGELOG.md
STATUS.md
README.md
```

At minimum:

```
What changed
What works
How to run it
What comes next
```

---

# 96. NO COMMIT POLICY

The implementation agent must NEVER commit automatically.

The user will review changes first.

Correct workflow:

```
Implement
   ↓
Test
   ↓
Update documentation
   ↓
Report
   ↓
STOP
   ↓
User reviews
   ↓
User decides whether to commit
```

---

# 97. NO PUSH POLICY

Never push to GitHub automatically.

Only perform a push when explicitly instructed.

---

# 98. FINAL PRINCIPLE

Build ORCA as a real engineering system.

Do not optimize for:

```
"It looks like a prototype."
```

Optimize for:

```
"The architecture is correct,
 the implementation is real,
 the data is traceable,
 the agents are meaningful,
 the results are explainable,
 and the system can continue growing."
```

The prototype is simply the first visible checkpoint of the complete ORCA
architecture.

---

# 99. AGENT BEHAVIOR SUMMARY

Every development action should follow:

```
READ
  ↓
UNDERSTAND
  ↓
PLAN
  ↓
IMPLEMENT
  ↓
TEST
  ↓
VERIFY
  ↓
DOCUMENT
  ↓
REPORT
  ↓
STOP
```

Never:

```
Guess
Fabricate
Hardcode critical intelligence
Ignore architecture
Commit automatically
Push automatically
Hide failures
Skip milestone documentation
```

---

# 100. FINAL INSTRUCTION

ORCA is being built incrementally toward its complete intended architecture.

Every implementation decision must prioritize:

```
Correctness
Modularity
Reliability
Explainability
Security
Maintainability
Reproducibility
Evidence
Testability
```

When uncertain, inspect the existing documentation and code first.

When a decision would materially change the architecture, stop and ask.

When a milestone is complete:

```
Update CHANGELOG.md
Update STATUS.md
Update README.md
Report what was built
Report what ORCA currently is
Report tests
Report current status
Report the next milestone
DO NOT COMMIT
DO NOT PUSH
STOP
```

