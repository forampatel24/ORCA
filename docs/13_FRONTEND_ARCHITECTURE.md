# ORCA — Frontend Architecture

**Project Name:** ORCA  
**Document:** Frontend Architecture  
**Document ID:** ORCA-FRONTEND-13  
**Version:** 1.0  
**Status:** FROZEN BASELINE  
**Scope:** Frontend Architecture, UI, UX, Maps, Chat, Visualizations, Alerts, Multilingual Interface and Backend Integration

---

# 1. Purpose

The ORCA frontend provides the user-facing interface for the Marine Intelligence Platform.

It must allow users to:

- Ask natural-language questions
- View conversational responses
- Explore PFZs
- View marine and weather conditions
- Explore interactive maps
- View hazards
- Check geofences and restricted regions
- View routes
- Understand risk assessments
- Inspect supporting evidence
- Receive alerts
- Explore historical and current marine information

The interface must make complex marine intelligence understandable to non-technical users.

---

# 2. Frontend Technology

Primary stack:

React
TypeScript
Vite
Tailwind CSS
MapLibre GL JS
React Query / TanStack Query
Axios
Zustand
Recharts
```

Optional supporting libraries:

```text
React Router
Lucide React
React Hook Form
Zod
```

---

# 3. Frontend Architecture

```text
                         ORCA FRONTEND
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
           CHAT             MAP             DASHBOARD
             │                │                │
             └────────────────┼────────────────┘
                              │
                         STATE LAYER
                              │
                       DATA / API LAYER
                              │
                              ▼
                           FASTAPI
                              │
                              ▼
                         ORCHESTRATOR
```

---

# 4. Design Principle

ORCA should not feel like:

```text
ChatGPT + a random map
```

It should feel like:

```text
Marine Intelligence Command Center
+
Conversational AI
+
Interactive Geospatial System
```

---

# 5. Main Interface

The primary ORCA interface should contain:

```text
┌───────────────────────────────────────────────┐
│ ORCA                         Alerts   Profile │
├───────────────┬───────────────────────────────┤
│               │                               │
│ Navigation    │         Main Workspace       │
│               │                               │
│ Chat          │                               │
│ Map           │                               │
│ PFZ           │                               │
│ Safety        │                               │
│ Routes        │                               │
│ Reports       │                               │
│               │                               │
└───────────────┴───────────────────────────────┘
```

The exact visual styling can evolve, but the information architecture remains fixed.

---

# 6. Primary Navigation

Main sections:

```text
Home
Ask ORCA
Marine Map
PFZ Intelligence
Safety
Routes
Reports
```

---

# 7. Home Dashboard

The home dashboard provides a high-level marine intelligence overview.

Possible components:

```text
Current Conditions
Nearby PFZs
Safety Status
Active Alerts
Weather Summary
Ocean Summary
Recent Queries
```

---

# 8. Ask ORCA

The conversational interface is the primary interaction mechanism.

Example:

```text
┌─────────────────────────────────────┐
│ Ask ORCA                            │
│                                     │
│ "Is it safe to fish tomorrow?"      │
│                                     │
│                     [Send]          │
└─────────────────────────────────────┘
```

---

# 9. Conversational Interface

The chat UI must support:

```text
User messages
ORCA responses
Streaming responses
Agent activity
Evidence
Maps
Charts
Risk cards
Suggested follow-up questions
```

---

# 10. Agent Activity

During a complex request, the interface can optionally display a compact execution indicator.

Example:

```text
ORCA is analyzing...

✓ Location resolved
✓ Weather analyzed
✓ Ocean conditions analyzed
✓ Hazard conditions checked
● Assessing overall risk
```

This visually demonstrates the agentic nature of ORCA.

---

# 11. Agent Activity Principle

Do not expose internal chain-of-thought.

The UI should show:

```text
What ORCA did
```

not:

```text
Private reasoning of the model
```

---

# 12. Streaming Response

For long-running requests:

```text
User
 ↓
ORCA
 ↓
Planning...
 ↓
Retrieving data...
 ↓
Analyzing...
 ↓
Response
```

The interface should update progressively.

---

# 13. Response Structure

A complex ORCA response may contain:

```text
Answer
↓
Risk Summary
↓
Key Findings
↓
Map
↓
Supporting Data
↓
Evidence
↓
Recommendation
↓
Follow-up Questions
```

---

# 14. Risk Card

Example:

```text
┌─────────────────────────────┐
│ MARINE RISK                 │
│                             │
│ HIGH                        │
│                             │
│ Main factors:               │
│ • High waves                │
│ • Strong winds              │
│ • Lightning risk            │
│                             │
│ [View details]              │
└─────────────────────────────┘
```

The actual risk value comes from the deterministic Risk Engine.

---

# 15. Evidence Section

Every important recommendation should allow the user to inspect supporting evidence.

Example:

```text
Why this recommendation?

• Wave conditions
• Wind forecast
• Lightning warning
• Marine advisory

[View evidence]
```

---

# 16. Evidence Detail

Evidence can include:

```text
Source
Timestamp
Data variable
Location
Observation / forecast
Confidence
```

---

# 17. Map System

The map is a core component of ORCA.

Technology:

```text
MapLibre GL JS
```

The map should support:

```text
Pan
Zoom
Markers
Popups
Polygons
Lines
Raster layers
Heatmaps
Multiple layers
```

---

# 18. Marine Map

The Marine Map provides a unified spatial view.

Possible layers:

```text
PFZ
SST
Chlorophyll
Waves
Wind
Currents
Tides
Lightning
Cyclones
Marine advisories
Protected areas
Restricted areas
International boundaries
Routes
```

---

# 19. Layer Control

Users should be able to toggle layers.

Example:

```text
MAP LAYERS

☑ PFZ
☑ Weather
☐ SST
☐ Chlorophyll
☐ Waves
☐ Currents
☐ Lightning
☐ Cyclones
☐ Protected Areas
☐ Geofences
```

---

# 20. PFZ Visualization

PFZs should be visually distinguishable.

Each PFZ object can display:

```text
PFZ ID
Location
Date
Distance
Relevant ocean conditions
```

Clicking a PFZ opens detailed information.

---

# 21. PFZ Detail Panel

Example:

```text
Potential Fishing Zone

Location:
18.42° N, 72.91° E

Distance:
14.7 km

Observed conditions:
SST: ...
Chlorophyll: ...

[Analyze this PFZ]
[Get route]
[Check safety]
```

---

# 22. SST Layer

The frontend should support visualization of sea-surface temperature.

Possible representation:

```text
Raster layer
Heatmap
Color-scale legend
```

The frontend receives visualization configuration from the backend.

---

# 23. Chlorophyll Layer

The chlorophyll layer can visualize spatial concentration.

Users should be able to:

```text
Toggle layer
Inspect point
View value
View timestamp
Compare regions
```

---

# 24. Weather Layer

Possible weather visualization:

```text
Wind vectors
Weather markers
Forecast information
Rainfall overlays
```

---

# 25. Wave Layer

Possible information:

```text
Wave height
Wave direction
Wave period
```

The UI should allow users to inspect conditions at a location.

---

# 26. Hazard Layer

Hazards should be visually prominent.

Possible categories:

```text
Lightning
Cyclone
High waves
Strong winds
Heavy rainfall
Low visibility
Marine advisory
```

---

# 27. Hazard Marker

Example:

```text
⚠ Hazard

Type:
High Waves

Severity:
High

Valid:
08:00–14:00

Source:
Official advisory
```

Icons and colors may be finalized during UI implementation.

---

# 28. Geofence Visualization

The map should display relevant operational boundaries.

Examples:

```text
International maritime boundaries
Restricted waters
Marine protected areas
Ecologically sensitive areas
Other configured boundaries
```

---

# 29. Geofence Warning

If the user selects or approaches a restricted region:

```text
┌──────────────────────────────┐
│ GEOSPATIAL WARNING           │
│                              │
│ This route intersects a      │
│ restricted region.           │
│                              │
│ [View boundary]              │
└──────────────────────────────┘
```

---

# 30. Route Visualization

Routes should be displayed directly on the map.

Example:

```text
Origin
  ●
  │
  │ Route A
  │
  ● Destination
```

Alternative routes can be displayed when generated.

---

# 31. Route Comparison

Example:

```text
Route A
Distance: 42 km
Risk: Low
Time: 2h 15m

Route B
Distance: 37 km
Risk: Medium
Time: 1h 55m
```

The user can select the preferred route based on the system's scoring criteria.

---

# 32. Route Explanation

ORCA should explain why a route was selected.

Example:

```text
Recommended Route

This route was selected because:

• Lower hazard exposure
• Avoids restricted waters
• Lower expected wave conditions
• Acceptable travel distance
```

---

# 33. Dashboard Cards

Dashboard information can be represented through cards.

Examples:

```text
Nearby PFZs
Marine Risk
Weather
Ocean Conditions
Active Alerts
```

---

# 34. Weather Card

```text
WEATHER

Temperature: ...
Wind: ...
Rain: ...
Visibility: ...

Forecast:
[View forecast]
```

---

# 35. Ocean Card

```text
OCEAN CONDITIONS

SST: ...
Chlorophyll: ...
Wave Height: ...
Current: ...

[Explore Ocean]
```

---

# 36. Safety Dashboard

The Safety section provides:

```text
Current risk
Forecast risk
Active hazards
Marine advisories
Lightning
Cyclone information
Geofence status
```

---

# 37. Safety Timeline

The UI may show risk over time:

```text
Morning       Afternoon       Evening

 LOW            HIGH             MEDIUM
```

This allows users to identify safer operating windows.

---

# 38. Alert System

ORCA should support alerts for:

```text
Cyclone
Lightning
High waves
Strong winds
Marine advisories
Geofence warnings
Other configured hazards
```

---

# 39. Alert Center

Example:

```text
ALERTS

High Wave Warning
12 minutes ago

Lightning Risk
34 minutes ago

Restricted Area Nearby
1 hour ago
```

---

# 40. Alert Detail

Each alert should include:

```text
Type
Severity
Location
Valid time
Source
Recommended action
```

---

# 41. Notification Philosophy

Alerts should be:

```text
Relevant
Actionable
Evidence-backed
Time-aware
Location-aware
```

Avoid excessive notifications.

---

# 42. Reports

The Reports section allows users to access generated reports.

Examples:

```text
Fishing Intelligence Report
Marine Safety Report
Route Report
Ocean Analysis Report
Hazard Report
```

---

# 43. Report Viewer

Reports may contain:

```text
Summary
Maps
Charts
Risk assessment
Evidence
Data sources
Recommendations
```

---

# 44. Historical Analysis

ORCA should support historical visualizations where datasets permit.

Example:

```text
SST trend
Chlorophyll trend
PFZ trend
Marine condition trend
```

---

# 45. Time Controls

The map should support time-aware data.

Example:

```text
< Previous    [ 29 Aug 2026 ]    Next >
```

For forecast data:

```text
Now
+6h
+12h
+24h
+48h
```

The exact time range depends on available datasets.

---

# 46. Location Selection

Users should be able to provide location through:

```text
Search
Map click
Coordinates
Current device location
Saved location
```

---

# 47. Search

Example:

```text
Search location...

Mumbai
Goa
Kochi
Chennai
```

The backend resolves locations where necessary.

---

# 48. Map Interaction

Clicking a map location can trigger:

```text
Location details
Marine conditions
Weather
PFZ proximity
Hazards
Geofence status
```

---

# 49. Contextual Actions

When viewing a location:

```text
Analyze Location
Find Nearest PFZ
Check Safety
Find Safe Route
View Ocean Conditions
```

This creates a bridge between map and conversational workflows.

---

# 50. Chat + Map Synchronization

Chat and map should remain synchronized.

Example:

```text
User:
"Show the nearest PFZ."

Chat
 ↓
PFZ result

Map
 ↓
PFZ automatically highlighted
```

---

# 51. Conversational Map Control

ORCA should support commands such as:

```text
"Show PFZs near Goa."

"Show dangerous areas."

"Show chlorophyll."

"Show the route."

"Zoom into this area."
```

The Orchestrator generates the required visualization state.

---

# 52. Visualization State

The frontend should maintain:

```text
map center
zoom
active layers
selected feature
time range
route
hazards
```

---

# 53. Frontend State Management

Use:

```text
Zustand
```

for application-level state.

Potential stores:

```text
chatStore
mapStore
userStore
alertStore
uiStore
```

---

# 54. Server Data Management

Use:

```text
TanStack Query
```

for:

```text
API requests
Caching
Refetching
Loading states
Error states
Server-state synchronization
```

---

# 55. Axios

Axios provides the HTTP client layer.

Example architecture:

```text
React Component
      ↓
Hook
      ↓
API Client
      ↓
Axios
      ↓
FastAPI
```

---

# 56. API Client Structure

```text
frontend/
└── src/
    ├── api/
    │   ├── client.ts
    │   ├── chat.ts
    │   ├── pfz.ts
    │   ├── weather.ts
    │   ├── ocean.ts
    │   ├── hazards.ts
    │   ├── routes.ts
    │   └── knowledge.ts
```

---

# 57. Component Architecture

```text
src/
├── components/
│   ├── chat/
│   ├── map/
│   ├── dashboard/
│   ├── risk/
│   ├── alerts/
│   ├── routes/
│   ├── evidence/
│   └── common/
```

---

# 58. Page Architecture

```text
src/
└── pages/
    ├── Home.tsx
    ├── Chat.tsx
    ├── MarineMap.tsx
    ├── PFZ.tsx
    ├── Safety.tsx
    ├── Routes.tsx
    └── Reports.tsx
```

---

# 59. Routing

React Router can provide:

```text
/
 /chat
 /map
 /pfz
 /safety
 /routes
 /reports
```

---

# 60. Responsive Design

The interface should work on:

```text
Desktop
Laptop
Tablet
Mobile
```

The primary target is desktop/laptop because ORCA is a data-intensive intelligence platform.

---

# 61. Mobile Design

On smaller screens:

```text
Sidebar
   ↓
Bottom navigation / drawer
```

The map should remain usable.

---

# 62. Loading States

Every data-heavy component needs loading states.

Example:

```text
Loading marine conditions...
```

Avoid blank screens.

---

# 63. Error States

Example:

```text
Unable to retrieve weather data.

The external weather source is currently unavailable.

[Retry]
```

---

# 64. Empty States

Example:

```text
No PFZ information was found for this region
and time period.
```

---

# 65. Data Freshness

The UI should display timestamps where relevant.

Example:

```text
Updated:
29 Aug 2026, 10:30 AM
```

For forecasts:

```text
Forecast valid:
29 Aug 12:00–18:00
```

---

# 66. Source Visibility

Users should be able to see where important information originated.

Example:

```text
Source
Official Marine Dataset
Updated 2 hours ago
```

---

# 67. Confidence

Where appropriate, the UI can display:

```text
High confidence
Moderate confidence
Limited confidence
```

Confidence must come from the underlying system rather than being arbitrarily generated by the UI.

---

# 68. Multilingual Interface

ORCA should support Indian languages.

The architecture should allow:

```text
English
Hindi
Marathi
Gujarati
Tamil
Telugu
Kannada
Malayalam
Bengali
Other supported languages
```

The exact supported language list depends on model and dataset capabilities.

---

# 69. Language Consistency

If the user asks:

```text
"क्या समुद्र में जाना सुरक्षित है?"
```

ORCA should respond in Hindi.

If the user changes language:

```text
"Answer in Marathi."
```

the interface should follow the current request.

---

# 70. Accessibility

The frontend should support:

```text
Keyboard navigation
Readable typography
Sufficient contrast
Screen-reader-friendly labels
Accessible buttons
Accessible map controls
```

---

# 71. Visualization Principles

Charts and maps should prioritize:

```text
Clarity
Accuracy
Context
Timestamp
Units
Source
```

Avoid decorative visualizations that do not communicate useful information.

---

# 72. Chart Types

Supported chart types may include:

```text
Line chart
Bar chart
Scatter plot
Time-series chart
Risk timeline
```

---

# 73. Map Legend

Every data layer requiring interpretation should have a legend.

Example:

```text
SST

Low ───────── High
```

---

# 74. Units

The frontend must display units explicitly.

Examples:

```text
km
°C
m
m/s
knots
```

The backend maintains normalized values.

---

# 75. Frontend Security

The frontend must NOT contain:

```text
LLM API keys
Weather API keys
Satellite API secrets
Database passwords
MinIO credentials
Qdrant credentials
Redis credentials
```

These remain server-side.

---

# 76. Environment Variables

Frontend may contain only non-sensitive configuration.

Example:

```text
VITE_API_BASE_URL
```

Secrets must remain in the backend environment.

---

# 77. Frontend-to-Backend Communication

```text
React
 ↓
Axios
 ↓
FastAPI
 ↓
Authentication
 ↓
API Router
 ↓
Service
 ↓
Orchestrator / Database / Agent
```

---

# 78. Authentication State

The frontend should maintain:

```text
authenticated user
access token
session status
```

Sensitive authentication information should be handled using secure practices appropriate to the deployment architecture.

---

# 79. Error Boundary

React error boundaries should prevent a single component failure from breaking the entire application.

---

# 80. Performance

The frontend should optimize:

```text
Lazy loading
Map layer management
API caching
Pagination
Debounced search
Virtualized lists where needed
Image optimization
Code splitting
```

---

# 81. Map Performance

Large datasets should not simply be rendered as thousands of individual DOM elements.

Prefer:

```text
Vector tiles
GeoJSON where appropriate
Raster tiles
Server-side filtering
Clustering
Viewport-based queries
```

---

# 82. Data Loading Strategy

Do not load every dataset when the dashboard opens.

Instead:

```text
User opens map
       ↓
Load essential layers
       ↓
User enables SST
       ↓
Fetch/load SST
       ↓
User enables chlorophyll
       ↓
Fetch/load chlorophyll
```

---

# 83. Query Caching

Frequently requested data may be cached through TanStack Query and backend Redis.

Example:

```text
Same weather request
       ↓
Cache
       ↓
Avoid unnecessary external request
```

Freshness policies depend on the data type.

---

# 84. Frontend Logging

Client logs should avoid:

```text
API secrets
Tokens
Personal sensitive information
```

Errors should include request IDs where useful.

---

# 85. Frontend Testing

Testing should include:

```text
Unit tests
Component tests
API integration tests
Map interaction tests
Accessibility tests
End-to-end tests
```

---

# 86. Example End-to-End UX

User:

```text
"Which fishing zone is safest tomorrow morning?"
```

Frontend:

```text
User enters question
       ↓
POST /chat
       ↓
Streaming activity appears
       ↓
ORCA analyzes:
Weather
Ocean
Hazards
PFZ
Geofences
       ↓
Risk result arrives
       ↓
Map highlights candidate PFZs
       ↓
Risk comparison appears
       ↓
Final recommendation appears
       ↓
Evidence available
```

---

# 87. Example Final Interface

```text
┌────────────────────────────────────────────────────────┐
│ ORCA                               Alerts    Profile    │
├───────────────┬────────────────────────┬───────────────┤
│               │                        │               │
│ Ask ORCA      │       MAP              │ ANALYSIS      │
│               │                        │               │
│ "Safest PFZ   │    ● PFZ A             │ Risk: LOW     │
│ tomorrow?"    │         ╲              │               │
│               │          ╲ Route        │ PFZ A         │
│ ORCA:         │           ●            │ 24 km         │
│               │                        │               │
│ Recommended   │  [Layers]              │ Weather       │
│ PFZ A.        │                        │ Waves         │
│               │                        │ Wind          │
│ [Evidence]    │                        │               │
│ [Details]     │                        │ [View Report] │
│               │                        │               │
└───────────────┴────────────────────────┴───────────────┘
```

---

# 88. Frontend Design Goal

The final experience should make the user feel that:

```text
"I asked a question."

and ORCA:

"Understood what I meant,
found the relevant information,
analyzed it,
showed me where it applies,
explained why,
and gave me an actionable answer."
```

---

# 89. Frozen Frontend Principles

ORCA's frontend architecture officially follows these principles:

1. React + TypeScript + Vite is the frontend foundation.
2. Tailwind CSS is used for UI styling.
3. MapLibre GL JS is used for interactive geospatial visualization.
4. TanStack Query manages server state.
5. Zustand manages application state.
6. Axios provides the HTTP client layer.
7. The chat interface is a primary interaction mechanism.
8. The map is a primary intelligence interface.
9. Chat and map must remain synchronized.
10. PFZs must be spatially visualized.
11. Weather and ocean conditions must be visualizable.
12. Hazards must be clearly represented.
13. Geofences must be visually represented.
14. Routes must be displayed on the map.
15. Risk must be presented clearly.
16. Important recommendations must expose supporting evidence.
17. Data timestamps should be visible where relevant.
18. Sources should be visible for important information.
19. The frontend must never contain backend secrets.
20. Complex requests should support streaming progress.
21. Agent activity may be shown without exposing private model reasoning.
22. Loading, error and empty states are mandatory.
23. The interface must support multilingual interaction.
24. The interface must be responsive.
25. Accessibility must be considered.
26. Large geospatial datasets must be rendered efficiently.
27. Data should be loaded on demand where possible.
28. Server state should be cached appropriately.
29. The frontend must remain independent of database implementation.
30. FastAPI is the only primary backend interface exposed to the frontend.
31. The interface must prioritize decision-support clarity over decorative UI.
32. ORCA should visually combine conversational intelligence, geospatial intelligence and marine analytics into one system.
