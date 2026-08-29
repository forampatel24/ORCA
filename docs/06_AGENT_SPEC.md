# ORCA — Agent Specification

**Project Name:** ORCA  
**Document:** Agent Specification  
**Document ID:** ORCA-AGENT-06  
**Version:** 1.0  
**Status:** FROZEN BASELINE  
**Scope:** Complete Multi-Agent Intelligence System

---

# 1. Purpose

ORCA is an Agentic AI-powered Marine Intelligence Platform.

The agent architecture enables ORCA to:

- Understand natural-language marine queries
- Identify user intent
- Plan multi-step tasks
- Select appropriate tools
- Retrieve information from heterogeneous sources
- Correlate marine, weather, satellite, and geospatial information
- Perform deterministic analysis
- Assess marine risk
- Generate safe routes
- Check geofencing restrictions
- Retrieve supporting knowledge
- Generate explainable responses
- Present evidence through maps, charts, and structured information

The agents collaborate through an orchestrated workflow rather than operating as independent chatbots.

---

# 2. Core Agent Architecture

ORCA follows:

```text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │  ORCHESTRATOR   │
                  │      AGENT      │
                  └────────┬────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       Marine           Weather          Ocean
       Agent             Agent           Agent
          │                │                │
          └────────────────┼────────────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        Geospatial       Risk         Routing
          Agent         Agent          Agent
             │             │             │
             └─────────────┼─────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
                 RAG Agent   Visualization
                              Agent
                    │             │
                    └──────┬──────┘
                           ▼
                     REPORT AGENT
                           │
                           ▼
                         USER
````

---

# 3. Agent Design Principle

Each agent must have:

```text
ONE PRIMARY RESPONSIBILITY
        +
SPECIALIZED TOOLS
        +
STRUCTURED INPUT
        +
STRUCTURED OUTPUT
```

Agents should not duplicate responsibilities.

For example:

```text
Weather Agent
     ↓
Weather intelligence

Risk Agent
     ↓
Risk calculation

Routing Agent
     ↓
Route optimization
```

The Risk Agent should not independently fetch every weather dataset if the Weather Agent already provides the required structured information.

---

# 4. Agent Inventory

ORCA will use the following core agents:

| #  | Agent                         | Primary Responsibility            |
| -- | ----------------------------- | --------------------------------- |
| 1  | Orchestrator Agent            | Planning and coordination         |
| 2  | Marine Data Agent             | Marine/fisheries data             |
| 3  | Weather Intelligence Agent    | Weather conditions and forecasts  |
| 4  | Ocean Analytics Agent         | SST, chlorophyll, waves, currents |
| 5  | Geospatial Intelligence Agent | Spatial reasoning and geofencing  |
| 6  | Risk Assessment Agent         | Marine safety/risk analysis       |
| 7  | Routing Agent                 | Safe route optimization           |
| 8  | RAG / Knowledge Agent         | Knowledge and advisory retrieval  |
| 9  | Visualization Agent           | Map/chart output specification    |
| 10 | Reporting Agent               | Final explainable response        |
| 11 | Alert Agent                   | Proactive hazard detection        |

---

# 5. Orchestrator Agent

## Purpose

The Orchestrator is the central intelligence coordinator.

It determines:

```text
What does the user want?
        ↓
What information is required?
        ↓
Which agents are required?
        ↓
Which tools are required?
        ↓
In what order?
        ↓
How should results be combined?
```

---

## Responsibilities

The Orchestrator handles:

* Intent interpretation
* Task decomposition
* Agent selection
* Workflow planning
* Agent coordination
* Dependency management
* Result aggregation
* Missing-data handling
* Final workflow completion

---

## Example

User:

> "Is it safe to go fishing tomorrow morning near Ratnagiri?"

The Orchestrator may determine:

```text
1. Identify location
2. Resolve "tomorrow morning"
3. Retrieve weather
4. Retrieve wave conditions
5. Retrieve wind
6. Check cyclone/lightning hazards
7. Check relevant marine advisories
8. Perform spatial analysis
9. Calculate risk
10. Generate explanation
```

Possible workflow:

```text
Orchestrator
     │
     ├── Weather Agent
     │
     ├── Ocean Agent
     │
     ├── Marine Agent
     │
     ├── RAG Agent
     │
     └── Risk Agent
              │
              ▼
         Reporting Agent
```

---

# 6. Marine Data Agent

## Purpose

Handles marine and fisheries-related information.

---

## Responsibilities

* Retrieve PFZ information
* Retrieve fisheries-related datasets
* Analyze fishing-zone information
* Find nearby potential fishing zones
* Compare historical fishing conditions
* Provide marine productivity information

---

## Tools

Potential tools:

```text
get_pfz()
get_nearby_pfz()
get_fisheries_data()
get_productivity_data()
get_historical_marine_data()
```

---

## Output

Example:

```json
{
  "pfz_available": true,
  "zones": [
    {
      "location": "...",
      "distance_km": 18.4,
      "confidence": 0.87
    }
  ],
  "source": "...",
  "observation_time": "..."
}
```

---

# 7. Weather Intelligence Agent

## Purpose

Provides atmospheric and meteorological intelligence.

---

## Responsibilities

* Current weather
* Forecast weather
* Wind conditions
* Rainfall
* Temperature
* Atmospheric pressure
* Lightning information
* Severe-weather conditions

---

## Tools

```text
get_current_weather()
get_weather_forecast()
get_wind()
get_rainfall()
get_lightning()
get_weather_alerts()
```

---

## Output

```json
{
  "location": "...",
  "forecast_time": "...",
  "wind_speed": 28,
  "wind_direction": 240,
  "rainfall": 12,
  "lightning": true,
  "alerts": []
}
```

---

# 8. Ocean Analytics Agent

## Purpose

Handles oceanographic and Earth-observation information.

---

## Responsibilities

* Sea surface temperature analysis
* Chlorophyll analysis
* Wave conditions
* Ocean currents
* Ocean-condition trends
* Satellite-derived marine indicators
* Marine productivity indicators

---

## Tools

```text
get_sst()
get_chlorophyll()
get_wave_conditions()
get_ocean_currents()
get_ocean_forecast()
analyze_ocean_trend()
```

---

## Example

```text
SST
 +
Chlorophyll
 +
Ocean Conditions
 +
Historical observations
        ↓
Ocean Intelligence
```

---

# 9. Geospatial Intelligence Agent

## Purpose

Performs spatial reasoning.

---

## Responsibilities

* Coordinate resolution
* Distance calculation
* Spatial intersection
* Geofence checking
* Protected-area checking
* Maritime-boundary checking
* Hazard-zone analysis
* Spatial filtering

---

## Tools

```text
geocode_location()
calculate_distance()
find_nearby()
check_geofence()
check_protected_area()
check_maritime_boundary()
find_hazards_nearby()
check_route_intersection()
```

---

## Important Rule

The LLM does not perform spatial calculations itself.

Instead:

```text
Agent
  ↓
Geospatial Tool
  ↓
PostGIS / Shapely
  ↓
Exact Result
```

---

# 10. Risk Assessment Agent

## Purpose

Determines marine operational risk.

---

## Responsibilities

* Combine environmental hazards
* Calculate risk score
* Classify risk level
* Identify dominant risk factors
* Evaluate data confidence
* Provide structured reasoning factors

---

## Inputs

Potential inputs:

```text
Wind
Wave Height
Lightning
Cyclone
Rainfall
Current
Tide
Geofence
Marine Advisories
Route Conditions
```

---

## Processing

```text
Weather
   +
Ocean
   +
Hazards
   +
Geospatial Restrictions
   +
Marine Advisories
        ↓
   Risk Engine
        ↓
 Risk Assessment
```

---

## Output

```json
{
  "risk_score": 78,
  "risk_level": "HIGH",
  "factors": [
    "Strong wind",
    "High wave conditions",
    "Lightning activity"
  ],
  "confidence": 0.91
}
```

---

# 11. Routing Agent

## Purpose

Generates safer routes for vessels.

---

## Responsibilities

* Analyze origin/destination
* Generate candidate routes
* Identify hazards
* Avoid restricted areas
* Consider marine conditions
* Score candidate routes
* Select the safest feasible route

---

## Tools

```text
generate_route()
get_route_geometry()
calculate_route_distance()
check_route_hazards()
check_route_geofences()
score_route()
optimize_route()
```

---

## Route Architecture

```text
Origin
   +
Destination
   +
Marine Conditions
   +
Hazards
   +
Geofences
        ↓
Candidate Routes
        ↓
Constraint Filtering
        ↓
Risk Scoring
        ↓
Route Ranking
        ↓
Recommended Route
```

---

# 12. RAG / Knowledge Agent

## Purpose

Retrieves authoritative contextual knowledge.

---

## Responsibilities

* Search marine knowledge
* Retrieve advisories
* Retrieve safety information
* Retrieve regulations
* Retrieve fisheries knowledge
* Retrieve scientific documentation
* Provide supporting evidence

---

## Tools

```text
semantic_search()
retrieve_documents()
retrieve_advisory()
retrieve_regulation()
rerank_evidence()
```

---

## RAG Pipeline

```text
User Query
    ↓
Query Processing
    ↓
Embedding
    ↓
Qdrant
    ↓
Top-K Retrieval
    ↓
Reranking
    ↓
Relevant Evidence
```

---

# 13. Visualization Agent

## Purpose

Determines how analytical results should be represented visually.

It does not create arbitrary visualizations without analytical grounding.

---

## Responsibilities

Determine whether the response needs:

```text
Map
Chart
Route
Hazard Overlay
PFZ Layer
Time Series
Risk Indicator
Table
```

---

## Example

User:

> "Show me the safest fishing zones tomorrow."

Visualization Agent may return:

```json
{
  "visualizations": [
    {
      "type": "map",
      "layers": [
        "pfz",
        "hazards",
        "risk_zones"
      ]
    },
    {
      "type": "risk_chart",
      "data": "zone_comparison"
    }
  ]
}
```

---

# 14. Reporting Agent

## Purpose

Converts structured agent results into the final user-facing response.

---

## Responsibilities

* Summarize findings
* Explain reasoning
* Present evidence
* Explain uncertainty
* Mention data timestamps
* Provide recommendations
* Reference visualizations

---

## Example Output Structure

```text
Recommendation
      ↓
Why
      ↓
Conditions
      ↓
Risk
      ↓
Supporting Evidence
      ↓
Map / Chart
      ↓
Important Caveat
```

---

# 15. Alert Agent

## Purpose

Handles proactive safety intelligence.

---

## Responsibilities

* Monitor relevant conditions
* Detect hazardous changes
* Evaluate alert thresholds
* Identify affected regions
* Trigger notifications
* Provide alert reasoning

---

## Possible Alert Types

```text
Cyclone
Lightning
High Waves
Strong Winds
Heavy Rain
Restricted Zone
Marine Hazard
Route Hazard
```

---

# 16. Agent Collaboration

Agents communicate through structured state rather than uncontrolled text.

Example:

```text
Orchestrator
      │
      ▼
Weather Agent
      │
      ▼
WeatherResult
      │
      ▼
Ocean Agent
      │
      ▼
OceanResult
      │
      ▼
Geospatial Agent
      │
      ▼
SpatialResult
      │
      ▼
Risk Agent
      │
      ▼
RiskResult
      │
      ▼
Reporting Agent
```

---

# 17. Shared Agent State

The LangGraph state should conceptually contain:

```text
query
user_id
conversation_id
language
location
time_range
intent
plan
required_agents
agent_results
tool_results
evidence
risk_assessment
route
visualizations
final_response
errors
```

---

# 18. Agent State Example

```json
{
  "query": "Is it safe to fish tomorrow morning?",
  "language": "en",
  "location": {
    "latitude": 16.99,
    "longitude": 73.31
  },
  "time_range": {
    "start": "...",
    "end": "..."
  },
  "intent": "marine_safety",
  "agent_results": {},
  "risk_assessment": null,
  "evidence": [],
  "visualizations": []
}
```

---

# 19. Parallel Agent Execution

Independent tasks should execute in parallel.

Example:

```text
              Orchestrator
                   │
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
   Weather       Ocean      Marine
    Agent        Agent       Agent
       │           │           │
       └───────────┼───────────┘
                   ▼
              Risk Agent
```

This reduces latency.

---

# 20. Sequential Dependencies

Some tasks must happen sequentially.

Example:

```text
User Query
    ↓
Location Resolution
    ↓
Data Retrieval
    ↓
Spatial Analysis
    ↓
Risk Assessment
    ↓
Route Optimization
    ↓
Reporting
```

The Orchestrator determines the dependency graph.

---

# 21. Example: PFZ Query

User:

> "Where is the nearest potential fishing zone today?"

Workflow:

```text
Orchestrator
      ↓
Resolve User Location
      ↓
Marine Data Agent
      ↓
Retrieve PFZ Data
      ↓
Geospatial Agent
      ↓
Calculate Distances
      ↓
Rank PFZs
      ↓
Visualization Agent
      ↓
Reporting Agent
      ↓
User
```

---

# 22. Example: Marine Safety Query

User:

> "Is it safe to venture into the sea tomorrow morning?"

Workflow:

```text
Orchestrator
      │
      ├── Weather Agent
      │
      ├── Ocean Agent
      │
      ├── Marine Agent
      │
      ├── RAG Agent
      │
      └── Geospatial Agent
                 │
                 ▼
            Risk Agent
                 │
                 ▼
        Visualization Agent
                 │
                 ▼
          Reporting Agent
```

---

# 23. Example: Route Query

User:

> "Give me the safest route from my location to this fishing zone."

Workflow:

```text
Orchestrator
      ↓
Location Resolution
      ↓
Marine Agent
      ↓
Ocean Agent
      ↓
Weather Agent
      ↓
Geospatial Agent
      ↓
Routing Agent
      ↓
Risk Agent
      ↓
Visualization Agent
      ↓
Reporting Agent
```

---

# 24. Example: Geofence Query

User:

> "Am I approaching a restricted marine area?"

Workflow:

```text
Orchestrator
      ↓
Current Location
      ↓
Geospatial Agent
      ↓
PostGIS
      ↓
Boundary Analysis
      ↓
Risk / Alert Agent
      ↓
Reporting Agent
```

---

# 25. Multilingual Interaction

The user-facing system should support multilingual interaction.

Pipeline:

```text
User Query
    ↓
Language Detection
    ↓
Intent Understanding
    ↓
Agent Workflow
    ↓
Structured Results
    ↓
Response Generation
    ↓
Same Language as User
```

The internal agent state should preferably use language-independent structured representations.

---

# 26. Evidence-Based Reasoning

Every important recommendation should be associated with evidence.

Conceptually:

```text
Recommendation
      │
      ├── Weather Evidence
      ├── Ocean Evidence
      ├── Marine Evidence
      ├── Spatial Evidence
      └── Knowledge Evidence
```

This prevents unsupported recommendations.

---

# 27. Uncertainty Handling

Agents must not fabricate missing information.

If required data is unavailable:

```text
Data unavailable
      ↓
Agent reports missing data
      ↓
Orchestrator evaluates alternatives
      ↓
Final response explains limitation
```

Example:

```text
"Lightning data is unavailable for this region,
so the safety assessment has reduced confidence."
```

---

# 28. Tool Access Control

Each agent receives only the tools relevant to its role.

Example:

```text
Weather Agent
    ├── get_weather()
    ├── get_forecast()
    └── get_lightning()

Routing Agent
    ├── generate_route()
    ├── score_route()
    └── check_route_hazards()

RAG Agent
    ├── semantic_search()
    └── retrieve_evidence()
```

This reduces accidental tool misuse.

---

# 29. Deterministic vs LLM Responsibilities

## LLM Responsibilities

```text
Intent understanding
Planning
Reasoning over structured results
Tool selection
Agent coordination
Natural-language explanation
Multilingual response
```

## Deterministic System Responsibilities

```text
Database queries
GIS calculations
Distance
Spatial intersection
Risk calculations
Route generation
Data validation
Numerical calculations
```

---

# 30. Agent Failure Handling

If an agent fails:

```text
Agent Failure
      ↓
Record Error
      ↓
Orchestrator
      ↓
Retry / Alternative Tool / Graceful Degradation
```

The system should never silently replace missing data with fabricated information.

---

# 31. Agent Observability

Each agent execution should be recorded.

Example:

```text
Agent
Tool
Input
Output
Execution Time
Status
Error
Timestamp
```

This information is stored in:

```text
agent_runs
tool_runs
```

---

# 32. Agent Security

Agents should not have unrestricted access to infrastructure.

The principle is:

```text
Agent
  ↓
Allowed Tool
  ↓
Validated Input
  ↓
Service Layer
  ↓
Database/API
```

Agents should not directly execute arbitrary system commands.

---

# 33. Agentic AI Requirements Demonstrated

ORCA's architecture explicitly demonstrates:

```text
Autonomous Planning          ✓
Reasoning                    ✓
Tool Selection               ✓
Task Decomposition           ✓
Agent Collaboration          ✓
Parallel Execution           ✓
Conditional Workflows        ✓
Data Integration             ✓
Geospatial Reasoning         ✓
Evidence-Based Decisions     ✓
Explainability               ✓
```

---

# 34. Final Agent Architecture

```text
                         USER
                           │
                           ▼
                    ┌──────────────┐
                    │ ORCHESTRATOR │
                    └──────┬───────┘
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ▼                ▼                 ▼
       MARINE           WEATHER            OCEAN
        AGENT            AGENT             AGENT
          │                │                 │
          └────────────────┼─────────────────┘
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ▼                ▼                 ▼
    GEOSPATIAL           RAG             ALERT
       AGENT            AGENT            AGENT
          │                │                 │
          └────────────────┼─────────────────┘
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
              RISK               ROUTING
              AGENT               AGENT
                 │                   │
                 └─────────┬─────────┘
                           ▼
                    VISUALIZATION
                        AGENT
                           │
                           ▼
                      REPORTING
                        AGENT
                           │
                           ▼
                         USER
```

---

# 35. Final Agent Count

ORCA has **11 logical agents** in the frozen architecture:

```text
1.  Orchestrator Agent
2.  Marine Data Agent
3.  Weather Intelligence Agent
4.  Ocean Analytics Agent
5.  Geospatial Intelligence Agent
6.  Risk Assessment Agent
7.  Routing Agent
8.  RAG / Knowledge Agent
9.  Visualization Agent
10. Reporting Agent
11. Alert Agent
```

These are logical responsibilities.

They do NOT necessarily mean 11 separate servers, applications, or LLM instances.

They can operate as nodes within one LangGraph-based backend.

---

# 36. Final Principle

ORCA should not be built as:

```text
11 Chatbots
```

It should be built as:

```text
ONE INTELLIGENT SYSTEM

with

SPECIALIZED AGENT NODES
+
DETERMINISTIC TOOLS
+
SHARED STATE
+
DATA SERVICES
+
RAG
+
GEOSPATIAL ANALYTICS
```

The Orchestrator decides what needs to happen.

Specialized agents perform domain-specific reasoning.

Tools perform deterministic operations.

The Reporting Agent converts the verified results into an understandable answer.
