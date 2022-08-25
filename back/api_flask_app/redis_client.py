import asyncio
import typing
import logging
import aioredis
import orjson
import os


log = logging.getLogger(__name__)


class RedisClient():
    def __init__(self):

        log.info(f"CACHE CONFIG: Using Redis cache.")
        self.redis = aioredis.from_url(
            # "redis://redis:6379",
            os.environ["REDIS_URL"],
            db=None,
            decode_responses=True,
        )

        self.cache_telemetry = {
            "cache_hits_success": 0,
            "cache_hits_miss": 0,
            "cache_storage": 0,
        }

    async def get(self, key: str):
        res = await self.redis.get(key)
        if not res:
            self.cache_telemetry["cache_hits_miss"] += 1
            return []
        self.cache_telemetry["cache_hits_success"] += 1
        return orjson.loads(res)

    async def set(self, key: str, value: typing.List[str]):
        res = await self.redis.set(key, orjson.dumps(value))
        self.cache_telemetry["cache_storage"] += 1
