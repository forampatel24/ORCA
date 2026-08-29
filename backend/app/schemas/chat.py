"""Schemas - docs 12_API_SPEC POST /api/v1/chat."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    location: Optional[Location] = None
    language: Optional[str] = Field(default=None, max_length=10)

class Evidence(BaseModel):
    source: str
    title: str
    snippet: str
    metadata: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    language: str
    request_id: str
    evidence: List[Evidence] = []
    visualizations: List[Dict[str, Any]] = []
    risk: Optional[Dict[str, Any]] = None
    sources: List[str] = []
