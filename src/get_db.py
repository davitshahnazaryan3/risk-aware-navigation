"""
Connects to MongoDB server to retrieve component information, update locations
"""
from pymongo import MongoClient
import logging
import json
import redis
from fastapi import HTTPException

from src.config import settings


if settings.db_type == "local":
    CONNECTION_STRING = "mongodb://localhost"
else:
    CONNECTION_STRING = f"mongodb+srv://{settings.mongo_initdb_root_username}:{settings.mongo_initdb_root_password}" \
                        f"@cluster0.fnot2.mongodb.net/{settings.database_name}?retryWrites=true"


def connect_to_dabase(database_name: str, redis_key: str, client: redis.Redis = None):
    try:
        if client is not None:
            cache = client.get("inventory_" + redis_key)
            if cache is not None:
                db = json.loads(cache)
                logging.info("Connected to cached inventory database")
                return db, True

        cluster = MongoClient(CONNECTION_STRING)
        db = cluster[database_name]

    except Exception as e:
        logging.error(e.__class__.__name__, exc_info=True)
        return {"message": e.__class__.__name__}, False

    else:
        logging.info("Connected to inventory database")
        return db, False


def clear_redis_cache(redis_client):
    try:
        redis_client.flushdb()
        logging.info("Redis cache cleared!")
        return {"message": "Redis cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to clear Redis cache")
    