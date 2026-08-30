"""Ocean anomaly - docs 15 8 SST anomaly."""
from typing import Dict, Any

# Mock historical baselines - in production from 10y average per docs
BASELINES = {"sst": 27.0, "chlorophyll": 0.6}

def sst_anomaly(observed: float, baseline: float = None) -> Dict[str, Any]:
    b = baseline if baseline is not None else BASELINES["sst"]
    anomaly = observed - b
    flag = "ANOMALOUS" if abs(anomaly) > 1.5 else "VALID"
    return {"observed": observed, "baseline": b, "anomaly": round(anomaly,2), "unit": "C", "flag": flag}

def chlorophyll_anomaly(observed: float, baseline: float = None) -> Dict[str, Any]:
    b = baseline if baseline is not None else BASELINES["chlorophyll"]
    anomaly = observed - b
    return {"observed": observed, "baseline": b, "anomaly": round(anomaly,3), "unit": "mg/m3", "flag": "VALID" if abs(anomaly) < 1.0 else "ANOMALOUS"}
