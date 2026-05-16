import json
import redis.asyncio as redis
from config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


async def set_nullifier(nullifier: str, ttl: int = 3600 * 24) -> None:
    await redis_client.set(f"nullifier:{nullifier}", "1", ex=ttl)


async def has_nullifier(nullifier: str) -> bool:
    return await redis_client.exists(f"nullifier:{nullifier}") == 1


async def set_merkle_cache(process_id: str, data: dict, ttl: int = 3600) -> None:
    await redis_client.set(f"merkle:{process_id}", json.dumps(data), ex=ttl)


async def get_merkle_cache(process_id: str) -> dict | None:
    raw = await redis_client.get(f"merkle:{process_id}")
    return json.loads(raw) if raw else None


async def ping() -> bool:
    try:
        return await redis_client.ping()
    except Exception:
        return False
