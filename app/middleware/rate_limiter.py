import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from redis.asyncio import Redis


class RateLimiter:
    def __init__(
        self,
        redis_client: Redis,
        limit: int = 100,
        window: int = 60
    ):
        self.redis = redis_client
        self.limit = limit
        self.window = window

    async def _call_(self, request: Request, call_next): # <- change here
        client_ip = request.client.host if request.client else "unknown"
        if await self.is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."}
            )
        return await call_next(request)

    async def is_rate_limited(self, client_ip: str) -> bool:
        key = f"rate_limit:{client_ip}"
        current_time = time.time()

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(
                key,
                0,
                current_time - self.window
            )

            pipe.zadd(
                key,
                {str(current_time): current_time}
            )

            pipe.zcard(key)

            pipe.expire(
                key,
                self.window
            )

            results = await pipe.execute()

        request_count = results[2]

        return request_count > self.limit