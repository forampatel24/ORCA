# ORCA — Agent Orchestration

**Project Name:** ORCA
**Document:** Agent Orchestration
**Document ID:** ORCA-AGENT-11
**Version:** 1.0
**Status:** FROZEN BASELINE
**Scope:** Agent Coordination, Planning, Tool Selection, Execution, State, Memory, Error Handling and Evidence Synthesis

---

# 1. Purpose

The Agent Orchestration layer is the central decision-making and coordination layer of ORCA.

It converts a natural-language user request into an executable multi-agent workflow.

The orchestration system is responsible for:

- Understanding user intent
- Identifying required information
- Creating an execution plan
- Selecting appropriate agents
- Selecting appropriate tools
- Running independent tasks in parallel
- Running dependent tasks sequentially
- Managing agent state
- Handling failures
- Validating agent outputs
- Combining evidence
- Sending results to the final reasoning layer
- Producing an explainable response

---

# 2. Core Principle

ORCA is an agentic system.

The LLM should not simply answer:

```text
User
 ↓
LLM
 ↓
Answer
````

Instead:

```text
User
 ↓
Orchestrator
 ↓
Plan
 ↓
Agents
 ↓
Tools
 ↓
Data
 ↓
Analysis
 ↓
Evidence
 ↓
Synthesis
 ↓
Answer
```

---

# 3. Orchestration Architecture

```text
                         USER
                           │
                           ▼
                    CONVERSATION LAYER
                           │
                           ▼
                    ORCHESTRATOR
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
             PLANNER              STATE
                │                     │
                └──────────┬──────────┘
                           ▼
                    TASK DECOMPOSER
                           │
                           ▼
                   AGENT SELECTION
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
        Marine Agent   Weather Agent   Ocean Agent
            │              │              │
            ▼              ▼              ▼
          Tools          Tools          Tools
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                  RESULT VALIDATION
                           │
                           ▼
                  EVIDENCE SYNTHESIS
                           │
                           ▼
                     RISK / ROUTE
                      ANALYSIS
                           │
                           ▼
                     FINAL LLM
                           │
                           ▼
                         USER
```

---

# 4. Agentic Loop

The core ORCA loop is:

```text
OBSERVE
   ↓
UNDERSTAND
   ↓
PLAN
   ↓
ACT
   ↓
OBSERVE RESULTS
   ↓
VALIDATE
   ↓
REASON
   ↓
ACT AGAIN IF REQUIRED
   ↓
SYNTHESIZE
   ↓
RESPOND
```

---

# 5. Main Orchestrator

The Orchestrator is responsible for coordinating the complete request.

Responsibilities:

```text
Intent interpretation
Task planning
Agent selection
Tool selection
Dependency management
Execution management
State management
Error handling
Evidence aggregation
Final response coordination
```

---

# 6. Planner

The Planner converts the user's request into executable tasks.

Example:

User:

```text
"Is it safe to fish tomorrow near Mumbai?"
```

Planner:

```text
Task 1:
Resolve location

Task 2:
Retrieve weather forecast

Task 3:
Retrieve wave conditions

Task 4:
Retrieve wind conditions

Task 5:
Retrieve lightning hazards

Task 6:
Retrieve cyclone warnings

Task 7:
Retrieve marine advisories

Task 8:
Calculate risk

Task 9:
Generate explanation
```

---

# 7. Planning Must Be Dynamic

The planner should NOT use a fixed workflow for every question.

Example:

```text
"What is the nearest PFZ?"
```

requires:

```text
Location
+
PFZ
+
PostGIS
```

while:

```text
"Why is chlorophyll useful?"
```

requires:

```text
RAG
+
Scientific Knowledge
```

---

# 8. Task Graph

The planner should represent complex requests as a task graph.

Example:

```text
             Location
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
    Weather    Waves   Lightning
       │        │        │
       └────────┼────────┘
                ▼
           Risk Engine
                │
                ▼
           Explanation
```

---

# 9. Task Dependencies

Some tasks are independent.

Example:

```text
Weather
Waves
Lightning
Cyclone
```

can be retrieved simultaneously.

Other tasks depend on earlier results.

Example:

```text
Location
   ↓
Geofence Check
   ↓
Risk Assessment
```

---

# 10. Parallel Execution

Independent tasks should execute in parallel when possible.

```text
                 Orchestrator
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
    Weather         Waves       Lightning
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                  Risk Engine
```

Benefits:

```text
Lower latency
Better user experience
Efficient resource utilization
```

---

# 11. Sequential Execution

Dependent operations execute sequentially.

Example:

```text
User Location
      ↓
Determine Region
      ↓
Find Applicable Regulation
      ↓
Retrieve Regulation
      ↓
Interpret Regulation
```

---

# 12. Agent Selection

The Orchestrator selects agents based on task requirements.

Conceptually:

```text
Question
   ↓
Required Capabilities
   ↓
Agent Registry
   ↓
Selected Agents
```

---

# 13. Agent Registry

The system should maintain metadata for agents.

Example:

```json
{
  "agent": "weather_agent",
  "capabilities": [
    "weather_forecast",
    "wind_analysis",
    "rain_analysis"
  ]
}
```

---

# 14. Core ORCA Agents

The architecture contains specialized agents for:

```text
1. Orchestrator / Planner
2. Marine Intelligence Agent
3. Weather Intelligence Agent
4. Ocean Analytics Agent
5. Geospatial Agent
6. Hazard / Safety Agent
7. Risk Assessment Agent
8. Routing Agent
9. RAG / Knowledge Agent
10. Visualization Agent
11. Reporting Agent
12. User Interaction / Language Agent
```

The exact implementation may combine lightweight roles where separate agents are unnecessary.

---

# 15. Marine Intelligence Agent

Responsibilities:

```text
PFZ analysis
Fishing-zone intelligence
Marine condition correlation
Fishing productivity context
```

Tools may include:

```text
PFZ retrieval
Ocean condition retrieval
SST retrieval
Chlorophyll retrieval
```

---

# 16. Weather Intelligence Agent

Responsibilities:

```text
Weather retrieval
Forecast interpretation
Wind analysis
Rainfall analysis
Visibility analysis
Weather hazard detection
```

---

# 17. Ocean Analytics Agent

Responsibilities:

```text
SST analysis
Chlorophyll analysis
Wave analysis
Current analysis
Tide analysis
Ocean trend analysis
```

---

# 18. Geospatial Agent

Responsibilities:

```text
Coordinate resolution
Spatial queries
Distance calculations
Geofence checks
Protected-area checks
Boundary intersection
Spatial relationships
```

---

# 19. Hazard / Safety Agent

Responsibilities:

```text
Lightning
Cyclone
High waves
Strong wind
Severe weather
Marine advisories
Hazard aggregation
```

---

# 20. Risk Assessment Agent

The Risk Assessment Agent combines structured hazard information.

Inputs may include:

```text
Wind
Wave height
Wave period
Lightning
Cyclone
Rainfall
Visibility
Tides
Geofence restrictions
Marine advisories
```

Output:

```text
Risk level
Risk factors
Evidence
```

---

# 21. Risk Engine Boundary

The numerical risk calculation should be deterministic.

The LLM should not arbitrarily invent:

```text
Risk = 73%
```

Instead:

```text
Input measurements
       ↓
Defined rules / model
       ↓
Risk score
       ↓
Agent explanation
```

---

# 22. Routing Agent

Responsibilities:

```text
Route generation
Route evaluation
Hazard-aware route selection
Geofence avoidance
Marine-condition-aware route scoring
```

---

# 23. RAG Agent

Responsibilities:

```text
Knowledge retrieval
Query expansion
Metadata filtering
Vector search
Hybrid retrieval
Evidence selection
Citation metadata
```

The RAG architecture is defined separately in:

```text
10_RAG_ARCHITECTURE.md
```

---

# 24. Visualization Agent

Responsibilities:

```text
Map requirements
Chart requirements
Layer selection
Visualization configuration
Evidence visualization
```

It should produce structured visualization specifications rather than manually drawing maps through the LLM.

---

# 25. Reporting Agent

Responsibilities:

```text
Structured summaries
Marine reports
Safety reports
Evidence summaries
Operational recommendations
```

---

# 26. User Interaction Agent

Responsibilities:

```text
Language detection
Language consistency
Conversational context
Query clarification
User-friendly explanation
```

ORCA should support Indian regional languages where the selected models and data sources allow.

---

# 27. Tool Registry

Agents should access capabilities through tools.

Example:

```text
Tool Registry
├── get_pfz
├── get_weather
├── get_ocean_conditions
├── get_tides
├── get_hazards
├── check_geofence
├── calculate_distance
├── search_knowledge
├── calculate_route
└── generate_visualization
```

---

# 28. Tool Selection

The agent determines which tools are required.

Example:

```text
User:
"Find the nearest PFZ."

Required:

get_location()
+
get_nearest_pfz()
```

No weather agent is required unless the user asks for safety or conditions.

---

# 29. Tool Contracts

Every tool should define:

```text
Tool name
Description
Input schema
Output schema
Errors
Required permissions
Data source
Freshness
```

---

# 30. Structured Tool Output

Tools should return structured data.

Example:

```json
{
  "latitude": 18.52,
  "longitude": 72.88,
  "timestamp": "...",
  "source": "...",
  "value": 28.4
}
```

The exact schema will be defined in the API specification.

---

# 31. Agent Communication

Agents should communicate through structured messages.

Conceptually:

```text
Agent A
   ↓
Task Result
   ↓
Orchestrator
   ↓
Agent B
```

Agents should not depend on arbitrary natural-language messages for critical machine-to-machine information.

---

# 32. Shared State

The Orchestrator maintains request-level state.

Example:

```text
session_id
user_query
resolved_location
time_range
selected_agents
completed_tasks
failed_tasks
tool_results
evidence
risk_result
final_response
```

---

# 33. Conversation State

For multi-turn conversations:

```text
User:
"Show PFZs near Goa."

ORCA:
[results]

User:
"What about tomorrow?"

ORCA:
Understands that:
location = Goa
topic = PFZ
date = tomorrow
```

The system should not require the user to repeat all context.

---

# 34. Short-Term Memory

Short-term memory contains information relevant to the current conversation.

Examples:

```text
Current location
Current date range
Current vessel route
Previous question
Previous tool results
Current analysis
```

---

# 35. Long-Term Memory

Long-term user memory should be introduced only when justified.

Potential examples:

```text
Preferred language
Preferred units
Saved locations
User preferences
```

Sensitive information should not be stored unnecessarily.

---

# 36. Memory Boundary

Memory must not override current user input.

Example:

```text
Previous:
User prefers English

Current:
"Answer in Marathi."

Current request wins.
```

---

# 37. Context Resolution

The orchestrator should resolve references.

Example:

```text
User:
"Show me the nearest one."

Context:
Previously discussed PFZs

Resolved:
nearest PFZ
```

---

# 38. Ambiguity Handling

If essential information is missing:

```text
User:
"Is it safe tomorrow?"
```

If location is unavailable:

```text
ORCA:
"Which fishing location should I check?"
```

The system should ask only when the missing information is necessary.

---

# 39. Date Resolution

Relative expressions must be resolved.

Examples:

```text
today
tomorrow
tomorrow morning
this weekend
next week
```

The resolved time should be explicitly available to downstream agents.

---

# 40. Location Resolution

User location can be provided through:

```text
Coordinates
Named location
Map selection
Saved location
Device location
```

The system should convert the result into coordinates where required.

---

# 41. Agent Execution Lifecycle

```text
CREATED
   ↓
PLANNED
   ↓
READY
   ↓
RUNNING
   ↓
COMPLETED
```

Failure states:

```text
FAILED
RETRYING
CANCELLED
```

---

# 42. Retry Policy

Transient tool failures can be retried.

Example:

```text
API Failure
   ↓
Retry
   ↓
Retry
   ↓
Success
```

Repeated failures should eventually terminate rather than loop indefinitely.

---

# 43. Agent Timeout

Every tool/agent task should have a timeout.

Example:

```text
Task Started
     ↓
Timeout
     ↓
Cancel / Retry / Fallback
```

---

# 44. Failure Isolation

One failed agent should not necessarily terminate the entire request.

Example:

```text
Weather       → SUCCESS
Ocean         → SUCCESS
Lightning     → FAILED
Cyclone       → SUCCESS
```

ORCA may still respond while clearly stating the missing evidence.

---

# 45. Source Degradation

If an external source becomes unavailable:

```text
Primary Source
      ↓
Unavailable
      ↓
Fallback Source
      ↓
Continue
```

Fallbacks should only be used where their data quality is acceptable.

---

# 46. No Fabrication

If required data is unavailable:

```text
DO NOT:
Invent the value.

DO:
State that the information could not be retrieved.
```

---

# 47. Result Validation

Agent results should be validated before being passed into final reasoning.

Validation includes:

```text
Schema validation
Type validation
Range validation
Timestamp validation
Coordinate validation
Source validation
```

---

# 48. Evidence Aggregation

The Orchestrator gathers:

```text
Structured data
Spatial results
RAG evidence
Agent results
Risk calculations
Source metadata
```

into a unified evidence set.

---

# 49. Evidence Object

Conceptually:

```json
{
  "type": "weather",
  "source": "...",
  "timestamp": "...",
  "data": {},
  "agent": "weather_agent"
}
```

---

# 50. Evidence Traceability

Every important recommendation should be traceable.

```text
Recommendation
      ↓
Risk Result
      ↓
Inputs
      ↓
Tools
      ↓
Sources
```

---

# 51. Final Synthesis

The final reasoning layer receives:

```text
User Intent
+
Conversation Context
+
Agent Results
+
Structured Data
+
RAG Evidence
+
Risk / Route Results
```

It then generates the user-facing response.

---

# 52. Final LLM Responsibility

The final LLM should:

```text
Understand evidence
Explain findings
Summarize results
Communicate uncertainty
Answer in requested language
Present recommendations
```

It should not:

```text
Invent measurements
Override database results
Change risk calculations
Ignore geofence restrictions
Create unsupported citations
```

---

# 53. Example — Nearest PFZ

User:

```text
"Where is the nearest PFZ today?"
```

Execution:

```text
1. Resolve user location
2. Resolve date = today
3. Call PFZ tool
4. PostGIS performs spatial search
5. Retrieve nearest PFZ
6. Retrieve supporting PFZ metadata
7. Visualization Agent creates map specification
8. Final LLM explains result
```

---

# 54. Example — Safe Fishing

User:

```text
"Is it safe to fish tomorrow morning?"
```

Execution:

```text
1. Resolve location
2. Resolve tomorrow morning
3. Weather Agent
4. Ocean Agent
5. Hazard Agent
6. Advisory retrieval
7. Geospatial restrictions
8. Risk Engine
9. Evidence aggregation
10. Visualization
11. Final explanation
```

Parallel section:

```text
Weather ──────┐
Waves ────────┤
Lightning ────┤
Cyclone ──────┤
Tides ────────┤
Advisories ───┘
       ↓
   Risk Engine
```

---

# 55. Example — Productivity Decline

User:

```text
"Why has fish productivity declined here?"
```

Execution:

```text
1. Resolve location
2. Resolve historical time period
3. Retrieve PFZ history
4. Retrieve SST history
5. Retrieve chlorophyll history
6. Retrieve ocean conditions
7. Temporal alignment
8. Spatial alignment
9. Trend analysis
10. Correlation analysis
11. RAG scientific context
12. Ocean Analytics Agent
13. Final explanation
```

The final response must distinguish:

```text
Observed correlation
```

from:

```text
Proven causation
```

---

# 56. Example — Safe Route

User:

```text
"Give me the safest route to the fishing zone."
```

Execution:

```text
1. Resolve origin
2. Resolve destination
3. Generate candidate routes
4. Check geofences
5. Retrieve weather
6. Retrieve waves
7. Retrieve currents
8. Retrieve hazards
9. Score candidate routes
10. Select valid route
11. Generate map
12. Explain route selection
```

---

# 57. Agent Coordination Example

```text
                     ORCHESTRATOR
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
      WEATHER           OCEAN           HAZARD
       AGENT             AGENT            AGENT
          │               │                │
          ▼               ▼                ▼
      Weather API      PostGIS/API      Hazard DB
          │               │                │
          └───────────────┼────────────────┘
                          ▼
                    RISK AGENT
                          │
                          ▼
                    VISUALIZATION
                          │
                          ▼
                    FINAL RESPONSE
```

---

# 58. Dynamic Replanning

Agentic behavior requires the ability to change plans.

Example:

```text
Plan:
Retrieve weather
Retrieve waves
Calculate risk
```

If weather retrieval reveals:

```text
Cyclone warning active
```

the Orchestrator may dynamically add:

```text
Cyclone advisory retrieval
+
Additional hazard analysis
```

---

# 59. Replanning Loop

```text
Initial Plan
    ↓
Execute
    ↓
New Information
    ↓
Does it require additional work?
    │
   YES
    ↓
Replan
    ↓
Execute New Tasks
    ↓
Synthesize
```

---

# 60. Agent Autonomy

Agents should be autonomous within defined boundaries.

Example:

Weather Agent may:

```text
Select weather tool
Choose relevant time range
Validate result
Request fallback source
```

But it cannot:

```text
Modify database schema
Override risk engine
Change system policies
```

---

# 61. Tool Permissions

Each agent should have an allowed tool set.

Example:

```text
Weather Agent:
weather tools

Geospatial Agent:
PostGIS tools

RAG Agent:
Qdrant / knowledge tools

Risk Agent:
risk calculation tools
```

---

# 62. Preventing Agent Loops

The orchestrator must prevent:

```text
Agent A
 ↓
Agent B
 ↓
Agent A
 ↓
Agent B
 ↓
...
```

Use:

```text
Maximum iterations
Task IDs
Dependency graph
Execution budget
```

---

# 63. Execution Budget

Each request may have limits for:

```text
Maximum agent calls
Maximum tool calls
Maximum replans
Maximum execution time
Maximum LLM calls
```

This prevents runaway agent behavior.

---

# 64. Observability

Every execution should record:

```text
Request ID
Task ID
Agent
Tool
Start time
End time
Status
Input metadata
Output metadata
Error
```

Sensitive values should not be logged unnecessarily.

---

# 65. Agent Tracing

A complex request should be traceable as:

```text
Request
 ├── Task 1
 │    └── Tool A
 ├── Task 2
 │    ├── Tool B
 │    └── Tool C
 └── Task 3
      └── Agent D
```

---

# 66. Human Override

For high-impact operational decisions, the architecture should allow human oversight where required.

ORCA should be positioned as:

```text
Decision Support
```

rather than claiming autonomous control of real-world vessels.

---

# 67. Safety Principle

ORCA recommendations should include appropriate uncertainty when:

```text
Data is stale
Source is unavailable
Forecast confidence is low
Sources conflict
Location is uncertain
Required evidence is incomplete
```

---

# 68. Agentic AI Definition in ORCA

ORCA demonstrates agentic AI through:

```text
Intent understanding
        +
Planning
        +
Task decomposition
        +
Agent selection
        +
Tool selection
        +
Parallel execution
        +
Sequential execution
        +
Dynamic replanning
        +
Result validation
        +
Evidence synthesis
        +
Explainable response
```

---

# 69. What Makes ORCA Agentic?

A simple chatbot:

```text
Question
 ↓
LLM
 ↓
Answer
```

ORCA:

```text
Question
 ↓
Understand
 ↓
Plan
 ↓
Decompose
 ↓
Select agents
 ↓
Select tools
 ↓
Retrieve multiple sources
 ↓
Analyze
 ↓
Observe results
 ↓
Replan if required
 ↓
Validate
 ↓
Correlate
 ↓
Assess risk
 ↓
Generate evidence-backed response
```

This distinction is central to the project.

---

# 70. Final Orchestration Architecture

```text
                              USER
                                │
                                ▼
                     CONVERSATION / LANGUAGE
                                │
                                ▼
                         ORCHESTRATOR
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
          PLANNER             STATE             MEMORY
             │
             ▼
       TASK DECOMPOSER
             │
             ▼
       AGENT REGISTRY
             │
    ┌────────┼────────┬────────┬────────┐
    │        │        │        │        │
    ▼        ▼        ▼        ▼        ▼
 Marine   Weather   Ocean   Geospatial  RAG
 Agent    Agent     Agent    Agent      Agent
    │        │        │        │        │
    ▼        ▼        ▼        ▼        ▼
  Tools    Tools    Tools    Tools    Qdrant
    │        │        │        │        │
    └────────┼────────┴────────┼────────┘
             │                 │
             ▼                 ▼
        RESULT VALIDATION   EVIDENCE
             │                 │
             └────────┬────────┘
                      ▼
               CROSS-DATASET
                  ANALYSIS
                      │
             ┌────────┴────────┐
             ▼                 ▼
        RISK ENGINE       ROUTING ENGINE
             │                 │
             └────────┬────────┘
                      ▼
              VISUALIZATION
                      │
                      ▼
                FINAL LLM
                      │
                      ▼
                   USER
```

---

# 71. Frozen Orchestration Principles

ORCA's orchestration architecture officially follows these principles:

1. The Orchestrator is the central coordinator.
2. Complex requests are decomposed into tasks.
3. Tasks are represented as dependencies.
4. Independent tasks should execute in parallel.
5. Dependent tasks execute sequentially.
6. Agents are selected based on capabilities.
7. Tools are selected based on task requirements.
8. Agents communicate through structured results.
9. Request-level state is maintained by the orchestrator.
10. Multi-turn context must be preserved.
11. The system supports dynamic replanning.
12. Tool failures must be isolated.
13. Transient failures may be retried.
14. Infinite agent loops must be prevented.
15. Execution budgets must exist.
16. Agent outputs must be validated.
17. Important recommendations must retain provenance.
18. Deterministic calculations must remain outside the LLM.
19. The LLM must not fabricate missing data.
20. RAG, structured data, geospatial data and APIs must operate as complementary capabilities.
21. Agents must operate within defined tool boundaries.
22. ORCA is a decision-support system, not an autonomous vessel-control system.
23. The architecture must remain modular so agents and tools can be added or replaced.
