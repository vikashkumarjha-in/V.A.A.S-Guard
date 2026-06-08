import asyncio
import os
import json
import logging
from datetime import datetime
from typing import List

import httpx
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from redis.asyncio import Redis

from config import settings
from app.middleware.security import SecurityMiddleware
from app.middleware.rate_limiter import RateLimiter
from app.logging.event_logger import event_logger
from app.explainability.llm_explainer import llm_explainer
from app.models.schemas import ThreatEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="V.A.S Guard Proxy")


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =====================================================
# WebSocket Manager
# =====================================================

class ConnectionManager:

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
        except Exception as e:
            logger.error(f"WebSocket connect failed: {e}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):

        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)

        message_str = json.dumps(
            message,
            default=json_serializer
        )

        dead_connections = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception:
                dead_connections.append(connection)

        for conn in dead_connections:
            self.disconnect(conn)


manager = ConnectionManager()


# =====================================================
# Threat Explanation Worker
# =====================================================

async def process_threat_explanation(event_dict: dict):

    try:
        event = ThreatEvent(**event_dict)

        explanation = await llm_explainer.explain_threat(
            event
        )

        try:
            await event_logger.update_explanation(
                event.event_id,
                explanation
            )
        except Exception as mongo_error:
            logger.error(
                f"Mongo update failed: {mongo_error}"
            )

        event.explanation = explanation
        event.status = "Analyzed"

        await manager.broadcast(
            event.model_dump()
        )

    except Exception as e:
        logger.error(
            f"Threat explanation failed: {e}"
        )


# =====================================================
# Rate Limiter Wrapper
# =====================================================

class RateLimiterWrapper:

    def __init__(self):
        self.limiter = None

    async def is_rate_limited(self, ip):

        if not self.limiter:
            return False

        try:
            return await self.limiter.is_rate_limited(ip)

        except Exception as e:
            logger.error(
                f"Rate limiter error: {e}"
            )
            return False


rate_limiter_wrapper = RateLimiterWrapper()


# =====================================================
# Security Middleware
# =====================================================

app.add_middleware(
    SecurityMiddleware,
    rate_limiter=rate_limiter_wrapper,
    ws_manager=manager,
    background_processor=process_threat_explanation
)


# =====================================================
# Startup
# =====================================================

@app.on_event("startup")
async def startup_event():

    try:
        await event_logger.initialize()

    except Exception as e:
        logger.error(
            f"MongoDB initialization failed: {e}"
        )

    try:
        redis = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )

        rate_limiter_wrapper.limiter = RateLimiter(
            redis_client=redis,
            limit=100,
            window=60
        )

        app.state.redis = redis

        logger.info(
            f"Redis connected: {settings.REDIS_URL}"
        )

    except Exception as e:
        logger.error(
            f"Redis connection failed: {e}"
        )

    logger.info("V.A.S Guard started")


# =====================================================
# Shutdown
# =====================================================

@app.on_event("shutdown")
async def shutdown_event():

    if hasattr(app.state, "redis"):
        await app.state.redis.aclose()


# =====================================================
# Health Endpoint
# =====================================================

@app.get("/health")
async def health():
    return {"status": "ok"}


# =====================================================
# WebSocket Logs
# =====================================================

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):

    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except Exception:
        pass

    finally:
        manager.disconnect(websocket)


# =====================================================
# Dashboard Static Files
# =====================================================

if os.path.exists("static"):
    app.mount(
        "/dashboard",
        StaticFiles(
            directory="static",
            html=True
        ),
        name="dashboard"
    )


# =====================================================
# Reverse Proxy
# =====================================================

@app.api_route(
    "/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS"
    ]
)
async def proxy_handler(
    request: Request,
    path: str
):

    if (
        path == "health"
        or path == "ws/logs"
        or path.startswith("dashboard")
    ):
        return Response(status_code=404)

    target_url = (
        f"{settings.TARGET_URL}/{path}"
    )

    headers = dict(request.headers)
    headers.pop("host", None)

    params = dict(request.query_params)

    try:
        body = await request.body()
    except Exception:
        body = b""

    try:

        async with httpx.AsyncClient() as client:

            upstream_response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=params,
                content=body,
                timeout=settings.PROXY_TIMEOUT
            )

            excluded_headers = {
                "content-encoding",
                "transfer-encoding",
                "connection"
            }

            response_headers = {
                k: v
                for k, v in upstream_response.headers.items()
                if k.lower() not in excluded_headers
            }

            return StreamingResponse(
                upstream_response.aiter_raw(),
                status_code=upstream_response.status_code,
                headers=response_headers
            )

    except httpx.TimeoutException:

        return Response(
            content="Gateway Timeout",
            status_code=504
        )

    except Exception as e:

        logger.error(
            f"Proxy error: {e}"
        )

        return Response(
            content="Internal Server Error",
            status_code=500
        )


if __name__ == "__main__":

    import uvicorn

    port = int(
        os.environ.get("PORT", 10000)
    )

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port
    )