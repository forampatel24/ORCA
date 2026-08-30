"""Middleware - request_id + structlog + metrics - docs 18."""
import uuid, time, structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.metrics import record_request

log = structlog.get_logger()

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        start = time.time()
        # bind to context
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)
        duration = time.time() - start
        response.headers['X-Request-ID'] = request_id
        # metrics
        try:
            record_request(request.method, request.url.path, response.status_code, duration)
        except: pass
        log.info("request_completed", method=request.method, path=request.url.path, status=response.status_code, duration=round(duration,3), request_id=request_id)
        structlog.contextvars.clear_contextvars()
        return response
