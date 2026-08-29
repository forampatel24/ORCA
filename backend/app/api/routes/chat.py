"""Chat endpoint skeleton - docs 12_API_APEC POST /api/v1/chat."""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from app.api.deps import get_current_user

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


@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest, current_user = Depends(get_current_user)):
    # M4 will wire orchestrator here. Stub for M0 verification.
    import uuid

    return ChatResponse(
        conversation_id=req.conversation_id or str(uuid.uuid4()),
        response=f"[M3 stub] Received: '{req.message}'. Orchestrator not yet wired (M4).",
        language=req.language or "en",
        request_id=str(uuid.uuid4()),
    )

@router.post("/stream")
async def chat_stream(req: ChatRequest, current_user = Depends(get_current_user)):
    import asyncio
    import json
    
    async def generate_response():
        events = [
            {"event": "request_started", "data": {"message": req.message}},
            {"event": "planning_started", "data": {}},
            {"event": "task_created", "data": {"agent": "orchestrator"}},
            {"event": "response_ready", "data": {"text": f"[M3 stub] Streaming response for: {req.message}"}},
            {"event": "request_completed", "data": {}}
        ]
        for event in events:
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0.5)
            
    return StreamingResponse(generate_response(), media_type="text/event-stream")
