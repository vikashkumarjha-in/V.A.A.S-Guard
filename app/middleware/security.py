from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import json
import asyncio
from app.detection.sqli_engine import detect_sqli
from app.logging.event_logger import event_logger
from app.models.schemas import ThreatEvent

class SecurityMiddleware(BaseHTTPMiddleware):
    def _init_(self, app, rate_limiter, ws_manager, background_processor=None):
        super()._init_(app)
        self.rate_limiter = rate_limiter
        self.ws_manager = ws_manager
        self.background_processor = background_processor

    async def _call_(self, request: Request, call_next):
        path = request.url.path
        if path in ["/ws/logs", "/health"] or path.startswith("/dashboard"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        # 1. Rate Limiting
        if await self.rate_limiter.is_rate_limited(client_ip):
            await self._log_and_notify(request, "RateLimit", "Medium", "Too many requests from IP")
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})

        # 2. SQLi Detection in Query Params
        query_str = str(request.query_params)
        is_sqli, pattern = detect_sqli(query_str)
        if is_sqli:
            await self._log_and_notify(request, "SQLi", "High", f"SQLi detected in query: {pattern}")
            return JSONResponse(status_code=403, content={"detail": "Security breach detected"})

        # 3. SQLi Detection in Headers
        headers_str = json.dumps(dict(request.headers))
        is_sqli, pattern = detect_sqli(headers_str)
        if is_sqli:
            await self._log_and_notify(request, "SQLi", "High", f"SQLi detected in headers: {pattern}")
            return JSONResponse(status_code=403, content={"detail": "Security breach detected"})

        # 4. SQLi Detection in Body
        body = await request.body()
        if body:
            body_str = body.decode("utf-8", errors="ignore")
            is_sqli, pattern = detect_sqli(body_str)
            if is_sqli:
                await self._log_and_notify(request, "SQLi", "Critical", f"SQLi detected in body: {pattern}")
                return JSONResponse(status_code=403, content={"detail": "Security breach detected"})

            # Rebuild body so downstream can read it
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive

        return await call_next(request)

    async def _log_and_notify(self, request: Request, threat_type: str, severity: str, details: str):
        event_id = str(uuid.uuid4())
        try:
            body = await request.body()
            body_str = body.decode("utf-8", errors="ignore") if body else None
        except:
            body_str = "Could not read body"

        event = ThreatEvent(
            event_id=event_id,
            client_ip=request.client.host if request.client else "unknown",
            method=request.method,
            path=request.url.path,
            headers=dict(request.headers),
            query_params=dict(request.query_params),
            body=body_str,
            threat_type=threat_type,
            severity=severity,
            explanation=details
        )

        try:
            await event_logger.log_threat(event)
        except Exception:
            pass

        await self.ws_manager.broadcast(event.dict())

        if self.background_processor:
            asyncio.create_task(self.background_processor(event.dict()))