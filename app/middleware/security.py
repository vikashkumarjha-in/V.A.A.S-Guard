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

    def __init__(
        self,
        app,
        rate_limiter,
        ws_manager,
        background_processor=None
    ):
        super().__init__(app)

        self.rate_limiter = rate_limiter
        self.ws_manager = ws_manager
        self.background_processor = background_processor

    async def dispatch(self, request: Request, call_next):

        path = request.url.path

        if (
            path == "/health"
            or path == "/ws/logs"
            or path.startswith("/dashboard")
        ):
            return await call_next(request)

        client_ip = (
            request.client.host
            if request.client
            else "unknown"
        )

        # Rate Limiting
        if await self.rate_limiter.is_rate_limited(client_ip):
            await self._log_and_notify(
                request,
                "RateLimit",
                "Medium",
                "Too many requests from IP"
            )

            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )

        # Query inspection
        query_str = str(request.query_params)

        is_sqli, pattern = detect_sqli(query_str)

        if is_sqli:
            await self._log_and_notify(
                request,
                "SQLi",
                "High",
                f"SQLi detected in query: {pattern}"
            )

            return JSONResponse(
                status_code=403,
                content={"detail": "Security breach detected"}
            )

        # Header inspection
        headers_str = json.dumps(dict(request.headers))

        is_sqli, pattern = detect_sqli(headers_str)

        if is_sqli:
            await self._log_and_notify(
                request,
                "SQLi",
                "High",
                f"SQLi detected in headers: {pattern}"
            )

            return JSONResponse(
                status_code=403,
                content={"detail": "Security breach detected"}
            )

        # Body inspection
        body = await request.body()

        if body:

            body_str = body.decode(
                "utf-8",
                errors="ignore"
            )

            is_sqli, pattern = detect_sqli(body_str)

            if is_sqli:
                await self._log_and_notify(
                    request,
                    "SQLi",
                    "Critical",
                    f"SQLi detected in body: {pattern}"
                )

                return JSONResponse(
                    status_code=403,
                    content={"detail": "Security breach detected"}
                )

            # Rebuild body so downstream can read it
            async def receive():
                return {
                    "type": "http.request",
                    "body": body,
                    "more_body": False
                }

            request._receive = receive

        return await call_next(request)

    async def _log_and_notify(
        self,
        request: Request,
        threat_type: str,
        severity: str,
        details: str
    ):
        event_id = str(uuid.uuid4())

        try:
            body = await request.body()

            body_str = (
                body.decode("utf-8", errors="ignore")
                if body
                else None
            )

        except Exception:
            body_str = "Unable to read body"

        event = ThreatEvent(
            event_id=event_id,
            client_ip=request.client.host
            if request.client
            else "unknown",
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

        try:
            await self.ws_manager.broadcast(
                event.model_dump()
            )
        except Exception:
            pass

        if self.background_processor:
            asyncio.create_task(
                self.background_processor(
                    event.model_dump()
                )
            )
