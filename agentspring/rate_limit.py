from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from .config import settings
async def setup_rate_limiter(app):
    r = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)
    return r
