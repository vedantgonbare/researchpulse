# app/core/limiter.py
import redis
from fastapi import HTTPException, Request
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """
    Rate limiter dependency.
    Limits requests per user per time window.
    
    max_requests: how many requests allowed
    window_seconds: in what time period
    Default: 10 requests per 60 seconds per user
    """
    def limiter(request: Request):
        # Get user IP as identifier (before auth) or use token
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}:{request.url.path}"

        # Get current count
        current = redis_client.get(key)

        if current is None:
            # First request — set counter with expiry
            redis_client.setex(key, window_seconds, 1)
        elif int(current) >= max_requests:
            # Limit exceeded
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {max_requests} requests per {window_seconds} seconds."
            )
        else:
            # Increment counter
            redis_client.incr(key)

    return limiter