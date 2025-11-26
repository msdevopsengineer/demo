import redis.asyncio as redis
from app.core.config import settings
from fastapi import HTTPException, status

class RateLimitService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    async def check_rate_limit(self, key: str, limit: int, window: int):
        """
        Check if the key has exceeded the limit in the window.
        key: Unique identifier (e.g., user_id or ip)
        limit: Max attempts
        window: Time window in seconds
        """
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, window)
        
        if current > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

rate_limit_service = RateLimitService()
