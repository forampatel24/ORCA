"""ORCA FastAPI entrypoint - docs 03_ARCHITECTURE API Layer."""
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, chat

log = structlog.get_logger()

app = FastAPI(
    title="ORCA Marine Intelligence Platform",
    version="0.1.0",
    description="Agentic AI-powered Marine Intelligence Platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])


@app.get("/")
async def root():
    return {"service": "ORCA", "status": "running", "docs": "/docs"}


@app.on_event("startup")
async def on_startup():
    log.info("orca_startup", environment="development")
