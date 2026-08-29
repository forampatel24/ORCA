# ORCA — ML & Analytics Architecture

**Project Name:** ORCA
**Document:** ML & Analytics Architecture
**Document ID:** ORCA-ML-15
**Version:** 1.0
**Status:** FROZEN BASELINE

---

# 1. Purpose

The ML & Analytics layer provides the computational intelligence required to transform raw marine, meteorological, satellite and geospatial observations into meaningful features, scores, predictions and analytical results.

This layer works underneath the Agentic AI system.

Its responsibility is:

Raw Data
    ↓
Cleaning
    ↓
Feature Engineering
    ↓
Spatial / Temporal Analysis
    ↓
Analytics / ML
    ↓
Structured Results
    ↓
Agents
    ↓
Explanation / Recommendation

---

# 2. Core Principle

ORCA follows this separation:

DETERMINISTIC / ML SYSTEM
→ Calculates what the data says.

AGENT SYSTEM
→ Decides which analysis is required and coordinates tools.

LLM
→ Understands the user, explains results and generates natural-language responses.

Therefore:

LLM ≠ Marine Calculator

LLM ≠ Risk Engine

LLM ≠ GIS Engine

LLM ≠ Weather Forecast Model

LLM ≠ PFZ Detection Algorithm

---

# 3. Intelligence Architecture

                         USER
                           │
                           ▼
                    ORCHESTRATOR
                           │
                           ▼
                     AGENT SYSTEM
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Ocean Agent    Weather Agent   Geo Agent
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    ANALYTICS LAYER
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
  PFZ Analytics       Risk Engine        Spatial Engine
       │                   │                   │
       ▼                   ▼                   ▼
  Ocean Analytics    Hazard Analytics   Route Analytics
                           │
                           ▼
                    Structured Results
                           │
                           ▼
                         LLM
                           │
                           ▼
                    User Explanation

---

# 4. Technology Stack

Primary technologies:

Python
Pandas
NumPy
SciPy
Scikit-learn
GeoPandas
Shapely
Rasterio
xarray
PostGIS
SQLAlchemy

Visualization:

Plotly
Recharts
MapLibre

Optional advanced geospatial processing:

GDAL
PyProj

---

# 5. Analytics Categories

ORCA's analytics layer consists of:

1. Ocean Analytics
2. PFZ Analytics
3. Weather Analytics
4. Hazard Analytics
5. Spatial Analytics
6. Temporal Analytics
7. Marine Risk Scoring
8. Route Analytics
9. Anomaly Detection
10. Productivity Analysis
11. Correlation Analysis
12. Statistical Analysis

---

# 6. Ocean Analytics

Ocean analytics processes variables such as:

SST
Chlorophyll
Ocean currents
Wave conditions
Sea-state variables
Other available ocean observations

The system should normalize these variables before analysis.

---

# 7. SST Analytics

The system should support:

Current SST lookup
Spatial SST comparison
Temporal SST trends
SST anomaly detection
SST-based feature generation

Example:

Location A
SST = 27.4°C

Location B
SST = 24.8°C

The analytics engine can compare these values with historical and spatial context.

---

# 8. SST Anomaly

Where historical reference data exists:

SST Anomaly =
Observed SST − Historical Baseline SST

Example:

Observed:
28.1°C

Historical average:
26.8°C

Anomaly:
+1.3°C

The result should retain:

value
baseline
timestamp
location
unit

---

# 9. Chlorophyll Analytics

The system should support:

Chlorophyll concentration lookup
Spatial comparison
Temporal trends
Anomaly detection
Correlation with PFZ observations

---

# 10. Chlorophyll Anomaly

Where historical data exists:

Chlorophyll Anomaly =
Observed Chlorophyll − Historical Baseline

The system should support normalized anomaly representations where appropriate.

---

# 11. Ocean Feature Engineering

Potential features:

SST
SST anomaly
Chlorophyll
Chlorophyll anomaly
SST gradient
Chlorophyll gradient
Wave height
Wave period
Current velocity
Current direction
Distance to coast
Depth where available
Season
Month
Time of day

Only features supported by available datasets should be enabled.

---

# 12. Spatial Feature Engineering

Spatial features may include:

Distance to PFZ
Distance to coastline
Distance to hazard
Distance to geofence
Distance to protected area
Distance to destination
Distance to nearest safe region

---

# 13. Temporal Features

Potential temporal features:

Hour
Day
Month
Season
Forecast horizon
Observation age
Data freshness
Historical average
Rolling average
Trend
Rate of change

---

# 14. Temporal Windowing

Marine conditions should not always be treated as isolated observations.

The system may analyze:

Current
+6 hours
+12 hours
+24 hours
+48 hours

depending on dataset availability.

---

# 15. Spatial Correlation

ORCA should be able to compare variables spatially.

Example:

SST
       +
Chlorophyll
       +
PFZ
       ↓
Potential fishing suitability

This does not automatically imply fish presence.

The system must distinguish correlation from causation.

---

# 16. Temporal Correlation

The system may analyze whether changes in:

SST
Chlorophyll
Weather
Ocean conditions

correspond with changes in historical fishing/PFZ indicators where appropriate data exists.

---

# 17. Correlation Analysis

Possible statistical methods:

Pearson correlation
Spearman correlation
Cross-correlation
Rolling correlation

Method selection depends on variable characteristics.

---

# 18. Correlation Output

Example:

Variable A:
Chlorophyll

Variable B:
PFZ occurrence

Result:

Correlation:
0.64

Interpretation:

Moderate positive association.

The system must avoid presenting this as proof of causation.

---

# 19. PFZ Analytics

PFZ analytics is one of ORCA's central analytical components.

It should support:

PFZ identification
PFZ ranking
PFZ comparison
PFZ proximity analysis
PFZ suitability analysis
PFZ temporal analysis

---

# 20. PFZ Ranking

Candidate PFZs can be ranked using measurable factors.

Potential factors:

Ocean suitability
SST suitability
Chlorophyll suitability
Distance
Weather conditions
Wave conditions
Hazard exposure
Geofence constraints

---

# 21. PFZ Score

A normalized score can be constructed:

PFZ Score =
Weighted Ocean Score
+
Environmental Score
+
Safety Score
+
Accessibility Score

The exact weights must be configuration-driven rather than hard-coded inside the LLM.

---

# 22. Important Safety Principle

A high PFZ score does NOT automatically mean:

"Safe to fish."

Fishing productivity and marine safety are separate dimensions.

Therefore ORCA maintains:

Fishing Suitability

and

Marine Safety

as separate scores.

---

# 23. Fishing Suitability Score

Conceptually:

Fishing Suitability =
Ocean Conditions
+
PFZ Evidence
+
Environmental Indicators
+
Historical Indicators

The score must be normalized.

---

# 24. Marine Safety Score

Conceptually:

Safety Score =
Weather
+
Wave Conditions
+
Wind
+
Lightning
+
Cyclone
+
Marine Advisories
+
Geofencing

Safety constraints may override suitability.

---

# 25. Safety Override

Example:

PFZ suitability:
HIGH

Marine risk:
VERY HIGH

Final recommendation:

AVOID / DO NOT RECOMMEND

The system must never recommend a productive fishing region while ignoring a critical safety hazard.

---

# 26. Risk Engine

The Risk Engine is deterministic.

Inputs may include:

Wind
Wave height
Wave period
Lightning
Cyclone status
Rainfall
Visibility
Marine advisories
Geofence violations
Other configured hazards

---

# 27. Risk Categories

Initial categories:

LOW
MODERATE
HIGH
VERY_HIGH

The exact thresholds should be configuration-driven.

---

# 28. Risk Calculation

The Risk Engine may use:

Rule-based scoring
Weighted scoring
Threshold logic
Statistical models
ML models

The chosen method must be documented and reproducible.

---

# 29. Rule-Based Safety

Example:

IF
wave_height > configured_threshold

THEN

increase wave risk.

IF
official cyclone warning = active

THEN

increase cyclone risk.

IF
route intersects restricted region

THEN

geofence risk = critical.

---

# 30. Hazard Aggregation

Multiple hazards should be combined.

Example:

Wind:
Moderate

Waves:
High

Lightning:
High

Cyclone:
None

Overall risk:

HIGH

The aggregation logic must be deterministic.

---

# 31. Hazard Severity

Each hazard should contain:

Type
Severity
Location
Start time
End time
Source
Confidence
Freshness

---

# 32. Weather Analytics

Weather analytics should support:

Current conditions
Forecast extraction
Forecast comparison
Wind analysis
Rainfall analysis
Visibility analysis
Storm detection
Hazard extraction

---

# 33. Forecast Comparison

ORCA may compare:

Current
Forecast
Historical

to determine:

Improvement
Deterioration
Anomaly

---

# 34. Weather Trend

Example:

08:00
Wind = 10 knots

12:00
Wind = 16 knots

16:00
Wind = 23 knots

The analytics engine can detect increasing wind conditions.

---

# 35. Wave Analytics

Potential variables:

Wave height
Wave direction
Wave period

Derived features:

Maximum expected wave
Average wave
Trend
Rapid increase
Exposure along route

---

# 36. Lightning Analytics

The system can analyze:

Lightning occurrence
Distance from location
Spatial density
Temporal activity
Forecast/alert status

---

# 37. Cyclone Analytics

Cyclone analysis may include:

Cyclone location
Track
Intensity
Forecast trajectory
Distance from fishing area
Distance from route
Expected hazard zone

---

# 38. Cyclone Distance

Example:

Cyclone center:
18.1°N, 70.2°E

Fishing location:
18.5°N, 72.0°E

Spatial engine calculates:

Distance = X km

This is a geospatial calculation, not an LLM calculation.

---

# 39. Geospatial Analytics

PostGIS should perform authoritative spatial operations where practical.

Examples:

ST_Distance
ST_Intersects
ST_Contains
ST_Within
ST_Buffer
ST_ClosestPoint

---

# 40. Geofence Analysis

Given:

Vessel location
Route
Restricted polygon

The spatial engine determines:

Inside
Outside
Approaching
Intersecting

---

# 41. Geofence Proximity

Example:

Current location:
12 km from restricted area

Warning threshold:
15 km

Result:

APPROACHING RESTRICTED AREA

---

# 42. Route Risk Analysis

A route should not only be optimized for distance.

Each route segment can be evaluated against:

Weather
Waves
Lightning
Cyclones
Geofences
Other hazards

---

# 43. Segment-Level Risk

Example:

Route:

A ── B ── C ── D

Segment A-B:
LOW

Segment B-C:
HIGH

Segment C-D:
LOW

Overall route risk:

HIGH

---

# 44. Route Score

Potential route score:

Route Score =
Distance Cost
+
Travel Time Cost
+
Weather Risk
+
Wave Risk
+
Hazard Exposure
+
Geofence Penalty

The weights are configurable.

---

# 45. Geofence Penalty

A route intersecting a prohibited region should receive a severe penalty or be rejected entirely depending on the boundary type.

---

# 46. Safe Route

The safest route is not necessarily:

Shortest route.

It is:

Best route satisfying safety and operational constraints.

---

# 47. Route Optimization

Possible algorithms:

Dijkstra
A*
Multi-objective pathfinding

The actual implementation depends on the routing network and available marine data.

---

# 48. Multi-Objective Routing

The routing engine may optimize:

Distance
Time
Risk

Conceptually:

Minimize:

Cost =
α(distance)
+
β(time)
+
γ(risk)

where:

α, β, γ

are configurable weights.

---

# 49. Anomaly Detection

ORCA may detect unusual marine conditions.

Possible methods:

Z-score
IQR
Rolling statistics
Isolation Forest
Local Outlier Factor

The initial implementation should prefer simpler interpretable methods.

---

# 50. Z-Score

For a variable:

z = (x - μ) / σ

Large absolute z-values may indicate anomalous observations.

Thresholds should be configurable.

---

# 51. IQR Detection

IQR:

Q3 − Q1

Potential outlier:

x < Q1 − 1.5(IQR)

or

x > Q3 + 1.5(IQR)

This is useful for basic dataset-quality and anomaly analysis.

---

# 52. Isolation Forest

Isolation Forest may be introduced for multivariate anomaly detection.

Potential features:

SST
Chlorophyll
Wave height
Wind
Current

It should not replace domain-specific safety rules.

---

# 53. Productivity Analysis

ORCA should support analysis of historical productivity where suitable data exists.

Potential inputs:

PFZ observations
Historical fishing data
Environmental variables
Season
Location

---

# 54. Productivity Decline Analysis

User:

"Why has productivity declined here?"

Potential pipeline:

Location
 ↓
Historical productivity
 ↓
SST trend
 ↓
Chlorophyll trend
 ↓
Ocean conditions
 ↓
Weather / environmental factors
 ↓
Statistical correlation
 ↓
Candidate explanations
 ↓
Agent explanation

---

# 55. Productivity Explanation

The system must distinguish:

Observed:
Chlorophyll decreased.

Observed:
PFZ frequency decreased.

Inference:
These changes are associated with reduced fishing suitability.

Do not claim:

"Chlorophyll caused the decline"

unless supported by appropriate causal analysis.

---

# 56. Statistical Analysis

ORCA may use:

Mean
Median
Variance
Standard deviation
Percentiles
Correlation
Trend analysis
Rolling averages
Anomaly scores

---

# 57. ML Usage Philosophy

Machine learning should be used where it provides genuine value.

Do not introduce ML simply to make the architecture appear more advanced.

---

# 58. Recommended ML Areas

Potential ML applications:

Anomaly detection
PFZ suitability prediction
Productivity prediction
Risk classification
Forecast refinement where training data exists

---

# 59. PFZ Prediction

If sufficient historical labeled data exists, ORCA may train a model predicting PFZ suitability.

Potential algorithms:

Random Forest
XGBoost
Gradient Boosting

The initial model should favor interpretability and robustness.

---

# 60. Model Features

Potential PFZ model features:

SST
Chlorophyll
SST anomaly
Chlorophyll anomaly
Season
Latitude
Longitude
Distance to coast
Ocean variables
Historical PFZ indicators

Only validated features should enter the final model.

---

# 61. Model Output

The model should output:

Prediction
Probability / confidence
Feature values
Model version
Timestamp

---

# 62. Explainable ML

Where ML models are used, ORCA should support feature importance.

Possible methods:

Permutation importance
SHAP

Example:

Prediction:

HIGH PFZ SUITABILITY

Important contributing features:

Chlorophyll
SST
Historical PFZ frequency

---

# 63. Model Registry

Models should have:

Model ID
Version
Training dataset
Training date
Features
Metrics
Parameters
Status

---

# 64. Model Versioning

Example:

pfz_model_v1
pfz_model_v2

The system must know which model generated a prediction.

---

# 65. Model Evaluation

Potential metrics:

Classification:

Accuracy
Precision
Recall
F1
ROC-AUC

Regression:

MAE
RMSE
R²

The metric depends on the model's task.

---

# 66. Safety Model Evaluation

Safety-critical decisions should not rely exclusively on an ML model.

Preferred:

Deterministic safety rules
+
Validated data
+
ML as supporting intelligence

---

# 67. Confidence

Each analytical result should expose confidence where meaningful.

Example:

Prediction:
High suitability

Confidence:
0.82

Confidence must reflect the actual analytical/modeling method.

---

# 68. Data Quality

Analytics should consider:

Missing values
Duplicate observations
Invalid coordinates
Invalid timestamps
Out-of-range values
Stale data
Sensor anomalies

---

# 69. Missing Data

Never silently replace critical missing information with fabricated values.

Possible approaches:

Interpolation
Forward fill
Statistical imputation
Model-based imputation

only where scientifically appropriate.

---

# 70. Data Quality Flags

Each analytical result may contain:

VALID
PARTIAL
STALE
MISSING
ANOMALOUS

---

# 71. Unit Normalization

Before analytics:

Temperature
→ °C

Distance
→ km

Speed
→ standardized internal unit

Wave height
→ meters

All transformations must be explicit.

---

# 72. Coordinate Reference Systems

Geospatial operations must use appropriate CRS definitions.

PostGIS should maintain spatial reference information.

Coordinate transformations should be handled explicitly.

---

# 73. Raster Analytics

Satellite-derived raster data may require:

Rasterio
xarray
GDAL

Operations may include:

Clipping
Resampling
Aggregation
Spatial statistics
Raster-to-vector conversion

---

# 74. Raster-to-Map Pipeline

Conceptually:

Satellite raster
 ↓
Processing
 ↓
Cloud / quality filtering
 ↓
Geospatial transformation
 ↓
Tile generation
 ↓
MapLibre
```

---

# 75. Analytics Service

Analytics should be separated from agents.

Example:

```text
backend/
└── app/
    ├── analytics/
    │   ├── pfz/
    │   ├── ocean/
    │   ├── weather/
    │   ├── hazards/
    │   ├── risk/
    │   ├── routing/
    │   ├── anomaly/
    │   └── productivity/
```

---

# 76. Analytics API

Agents should interact with analytics through structured services.

Example:

```text
analyze_pfz()
calculate_marine_risk()
analyze_ocean_conditions()
analyze_route_risk()
detect_anomalies()
analyze_productivity()
```

---

# 77. Structured Output

Example:

```json
{
  "location": {
    "latitude": 18.42,
    "longitude": 72.91
  },
  "pfz_score": 0.84,
  "safety_score": 0.31,
  "overall_risk": "HIGH",
  "factors": [
    "high_wave_conditions",
    "moderate_wind",
    "favorable_chlorophyll"
  ],
  "timestamp": "..."
}
```

---

# 78. Analytics → Agent

The agent receives structured information:

```text
PFZ Score = 0.84
Safety Score = 0.31
Risk = HIGH
Wave Risk = HIGH
Chlorophyll = Favorable
```

The agent then explains:

why the region is productive-looking

and

why it may still be unsafe.

---

# 79. Analytics → Visualization

Analytics outputs should contain enough metadata for visualization.

Example:

```text
value
unit
location
timestamp
source
confidence
geometry
```

---

# 80. Reproducibility

Every analytical result should ideally be reproducible from:

Input data
Parameters
Algorithm
Model version
Timestamp

---

# 81. Configuration

Thresholds and weights should be configuration-driven.

Example:

```text
risk_thresholds.yaml
pfz_weights.yaml
routing_weights.yaml
```

Avoid burying critical domain parameters inside code.

---

# 82. No Hidden LLM Calculations

The LLM must not silently invent:

Wave height
Risk percentage
Distance
SST
Chlorophyll
Coordinates
Travel time

These values must originate from tools, datasets or deterministic calculations.

---

# 83. Agent vs Analytics Responsibility

```text
AGENT

"What information do I need?"

"Which tool should I call?"

"How should I combine the results?"

"How should I answer the user?"



ANALYTICS

"What is the SST anomaly?"

"What is the route risk?"

"Does this route intersect a geofence?"

"What is the PFZ score?"

"What hazards exist?"

"What is the spatial distance?"
```

---

# 84. Example Full Analysis

User:

"Which fishing zone is safest tomorrow morning?"

ORCA:

1. Resolve location.
2. Determine tomorrow morning time window.
3. Retrieve candidate PFZs.
4. Retrieve weather forecast.
5. Retrieve ocean conditions.
6. Retrieve hazards.
7. Check geofences.
8. Calculate PFZ suitability.
9. Calculate marine safety.
10. Rank candidates.
11. Generate explanation.
12. Visualize candidates.
13. Return evidence.

---

# 85. Final Decision Layer

The final recommendation should combine:

```text
Productivity / suitability
+
Safety
+
Accessibility
+
Geospatial restrictions
+
Data confidence
```

Safety constraints have priority.

---

# 86. Analytics Failure Handling

If an analytical service fails:

```text
Service unavailable
        ↓
Do not fabricate result
        ↓
Return partial analysis
        ↓
Mark missing component
```

---

# 87. Analytics Monitoring

Monitor:

Execution time
Failure rate
Input quality
Output validity
Model performance
Data freshness

---

# 88. Future ML Expansion

Potential future capabilities:

Deep learning
Spatiotemporal forecasting
Graph neural networks
Advanced ocean modeling
Satellite image segmentation
Learned route optimization
Fish species prediction

These are NOT mandatory components of the initial architecture.

---

# 89. Initial Implementation Priority

Priority 1:

PostGIS spatial analytics
Ocean feature engineering
Weather feature extraction
Hazard analysis
Deterministic risk engine
PFZ scoring
Route risk calculation

Priority 2:

Historical analysis
Anomaly detection
Correlation analysis
Productivity analysis

Priority 3:

ML-based prediction

Priority 4:

Advanced deep learning

---

# 90. Frozen ML Architecture

ORCA officially follows these principles:

1. LLMs do not perform authoritative numerical calculations.
2. Agents coordinate analytical tools.
3. Python is the primary analytics language.
4. Pandas handles tabular analytics.
5. NumPy handles numerical computation.
6. SciPy handles statistical computation where required.
7. Scikit-learn handles classical ML.
8. GeoPandas and Shapely support geospatial processing.
9. Rasterio/xarray support raster and multidimensional environmental data.
10. PostGIS performs authoritative spatial database operations.
11. PFZ suitability and marine safety remain separate concepts.
12. Safety can override fishing suitability.
13. Risk scoring must be deterministic/reproducible.
14. Critical thresholds must be configuration-driven.
15. Historical baselines should be used where sufficient data exists.
16. Correlation must not automatically be presented as causation.
17. ML is introduced only where sufficient training data exists.
18. ML predictions must expose model/version metadata.
19. Explainable ML should be used for important predictions.
20. Safety-critical decisions must not depend solely on ML predictions.
21. Data freshness must be tracked.
22. Missing critical data must not be fabricated.
23. All important calculations must be reproducible.
24. Analytics outputs must be structured.
25. Agents consume analytics results and provide contextual explanation.
26. Visualization consumes structured analytical outputs.
27. The analytics layer remains independent from the frontend.
28. The analytics layer remains independent from the LLM provider.
29. Every major analytical result should retain source/time/location context.
30. The architecture must support future ML expansion without requiring a redesign of the agent system.
