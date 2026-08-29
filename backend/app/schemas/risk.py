"""Risk schema stub (M6 placeholder)."""
from pydantic import BaseModel
from typing import List

class RiskFactor(BaseModel):
    factor: str
    contribution: float

class RiskResponse(BaseModel):
    risk_score: float
    risk_level: str
    factors: List[RiskFactor]
    timestamp: str | None = None
