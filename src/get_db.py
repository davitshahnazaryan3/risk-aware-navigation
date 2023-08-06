"""
Connects to MongoDB server to retrieve component information, update locations
"""
from pymongo import MongoClient
import logging
import json
import redis

from src.config import settings


CONNECTION_STRING = f"mongodb+srv://{settings.mongo_user}:{settings.mongo_password}" \
                    f"@cluster0.fnot2.mongodb.net/{settings.database_name}?retryWrites=true"
# CONNECTION_STRING = "mongodb://localhost"


def get_database(database_name: str, redis_key: str, client: redis.Redis = None):
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
