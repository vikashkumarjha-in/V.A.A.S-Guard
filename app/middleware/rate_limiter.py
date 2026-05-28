import time
from redis.asyncio import Redis
from config import settings

class RateLimiter:
    def __init__(self, redis_client: Redis, limit: int = 100, window: int = 60):
        self.redis = redis_client
        self.limit = limit
        self.window = window

    async def is_rate_limited(self, client_ip: str) -> bool:
        key = f"rate_limit:{client_ip}"
        current_time = time.time()

        # Using a sliding window with Redis sorted sets
        async with self.redis.pipeline(transaction=True) as pipe:
            # Remove old entries
            pipe.zremrangebyscore(key, 0, current_time - self.window)
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            # Count requests in window
            pipe.zcard(key)
            # Set expiry to keep redis clean
            pipe.expire(key, self.window)

            results = await pipe.execute()

        request_count = results[2]
        return request_count > self.limit
