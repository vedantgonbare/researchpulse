# app/services/cache.py
import redis
import json
from app.core.config import settings

# Connect to Redis
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_cached(key: str) -> dict | list | None:
    """Get data from Redis cache. Returns None if not found."""
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def set_cache(key: str, value: dict | list, expire_seconds: int = 3600):
    """Save data to Redis. Expires after 1 hour by default."""
    redis_client.setex(key, expire_seconds, json.dumps(value))

def delete_cache(key: str):
    """Delete a specific cache key."""
    redis_client.delete(key)

def delete_pattern(pattern: str):
    """Delete all keys matching a pattern. e.g. 'search:*'"""
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)