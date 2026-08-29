"""Chat endpoint skeleton - docs 12_API_APEC POST /api/v1/chat."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    location: Optional[dict] = None  # {"lat": 19.1, "lon": 72.8}
    language: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    language: str
    request_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # M4 will wire orchestrator here. Stub for M0 verification.
    import uuid

    return ChatResponse(
        conversation_id=req.conversation_id or str(uuid.uuid4()),
        response=f"[M0 scaffold] Received: '{req.message}'. Orchestrator not yet wired (M4).",
        language=req.language or "en",
        request_id=str(uuid.uuid4()),
    )
