import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as redis

from app.config import settings

# Global Redis Client
redis_client: redis.Redis | None = None

async def setup_redis():
    """Initialize Redis connection pool."""
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.aclose()

# Atomic Token Bucket Lua Script for Redis
TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local rate = tonumber(ARGV[1])      -- tokens added per minute
local capacity = tonumber(ARGV[2])  -- max bucket size
local now = tonumber(ARGV[3])       -- current timestamp

local info = redis.call('HMGET', key, 'tokens', 'last_refresh')
local tokens = tonumber(info[1])
local last_refresh = tonumber(info[2])

-- Initialize if it's a new key
if tokens == nil then
    tokens = capacity
    last_refresh = now
end

-- Calculate token refill based on time passed
local time_passed = math.max(0, now - last_refresh)
tokens = math.min(capacity, tokens + time_passed * (rate / 60))

-- Check if we have enough tokens (1 request = 1 token)
if tokens >= 1 then
    tokens = tokens - 1
    redis.call('HMSET', key, 'tokens', tokens, 'last_refresh', now)
    redis.call('EXPIRE', key, 120) -- Keep alive for 2 mins
    return 1 -- Allowed
else
    redis.call('HMSET', key, 'tokens', tokens, 'last_refresh', now)
    redis.call('EXPIRE', key, 120)
    return 0 -- Rate limited
end
"""

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not redis_client:
            # Fail-open if Redis is down
            return await call_next(request)

        # Identify user by IP (or extract from Authorization token if needed)
        client_id = request.client.host if request.client else "unknown"
        bucket_key = f"rate_limit:{client_id}"
        
        try:
            # Execute the Lua script
            is_allowed = await redis_client.eval(
                TOKEN_BUCKET_LUA, 
                1, # Number of keys
                bucket_key, 
                settings.RATE_LIMIT_REQUESTS_PER_MINUTE, # Rate
                settings.RATE_LIMIT_REQUESTS_PER_MINUTE, # Capacity
                time.time() # Now
            )
            
            if not is_allowed:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Too Many Requests. Rate limit exceeded."},
                    headers={"Retry-After": "60"}
                )
                
        except Exception:
            # If Redis errors out, log it but don't block the user (fail-open)
            pass

        return await call_next(request)