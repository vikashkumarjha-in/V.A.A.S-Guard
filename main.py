import asyncio
import os
import json
import logging
from datetime import datetime
from typing import List

import httpx
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from redis.asyncio import Redis

from config import settings
from app.middleware.security import SecurityMiddleware
from app.middleware.rate_limiter import RateLimiter
from app.logging.event_logger import event_logger
from app.explainability.llm_explainer import llm_explainer
from app.models.schemas import ThreatEvent

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="V.A.A.S Guard Proxy")

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
        except Exception as e:
            logger.error(f"WS accept failed: {e}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)

        msg_str = json.dumps(message, default=json_serial)
        for connection in self.active_connections:
            try:
                await connection.send_text(msg_str)
            except Exception:
                pass

manager = ConnectionManager()

# Background Tasks
async def process_threat_explanation(event_dict: dict):
    try:
        event = ThreatEvent(**event_dict)
        explanation = await llm_explainer.explain_threat(event)
        try:
            await event_logger.update_explanation(event.event_id, explanation)
        except Exception as e:
            logger.error(f"Mongo update failed: {e}")

        event.explanation = explanation
        event.status = "Analyzed"
        await manager.broadcast(event.dict())
    except Exception as e:
        logger.error(f"LLM task failed: {e}")

class RateLimiterWrapper:
    def __init__(self):
        self.limiter = None
    async def is_rate_limited(self, ip):
        if self.limiter:
            try:
                return await self.limiter.is_rate_limited(ip)
            except Exception:
                return False
        return False

rate_limiter_wrapper = RateLimiterWrapper()

# Middleware Registration
app.add_middleware(
    SecurityMiddleware,
    rate_limiter=rate_limiter_wrapper,
    ws_manager=manager,
    background_processor=process_threat_explanation
)

# Lifecycle
@app.on_event("startup")
async def startup_event():
    try:
        await event_logger.initialize()
    except Exception as e:
        logger.error(f"MongoDB offline: {e}")

    try:
        redis = Redis.from_url(settings.REDIS_URL)
        rate_limiter_wrapper.limiter = RateLimiter(redis)
        app.state.redis = redis
        logger.info(f"Redis linked: {settings.REDIS_URL}")
    except Exception as e:
        logger.error(f"Redis link failed: {e}")

    logger.info("V.A.A.S Guard Engine Running")

@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, "redis"):
        await app.state.redis.close()

# Routes
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        manager.disconnect(websocket)

# Static Dashboard
if os.path.exists("static"):
    app.mount("/dashboard", StaticFiles(directory="static", html=True), name="static")

# Transparent Proxy
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_handler(request: Request, path: str):
    if path.startswith("dashboard") or path == "health" or path == "ws/logs":
         return Response(status_code=404)

    url = f"{settings.TARGET_URL}/{path}"
    method = request.method
    headers = dict(request.headers)
    headers.pop("host", None)
    params = dict(request.query_params)

    try:
        content = await request.body()
    except Exception:
        content = b""

    async with httpx.AsyncClient() as client:
        try:
            proxy_response = await client.request(
                method, url, params=params, headers=headers, content=content,
                timeout=settings.PROXY_TIMEOUT
            )
            return StreamingResponse(
                proxy_response.aiter_raw(),
                status_code=proxy_response.status_code,
                headers=dict(proxy_response.headers)
            )
        except httpx.TimeoutException:
            return Response(content="Gateway Timeout", status_code=504)
        except Exception as e:
            logger.error(f"Proxy fail: {e}")
            return Response(content="Internal error", status_code=500)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
