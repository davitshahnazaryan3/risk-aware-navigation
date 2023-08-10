import json
from datetime import timedelta
from bson import json_util
from fastapi import FastAPI
import redis
import logging
from src.config import settings

from .schemas import SensorInput, SensorInput1
from .get_db import get_database
from .risks import Risk, update_risks
from .utils import requests_retry_session

app = FastAPI()
redis_client = redis.Redis(host=settings.redis_host)

logging.basicConfig(level=logging.DEBUG, filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")

MAP_A = "2-Navigation_map_v1.0"
MAP_B = "2-NavigationFile"


def cache_data(key, data, seconds=60):
    redis_client.set(key, json.dumps({key: data}))
    redis_client.expire(key, timedelta(seconds=seconds))


def _get_map_name(map_name):
    redis_inventory_key = map_name

    if map_name is None:
        map_name = settings.map_name
        redis_inventory_key = settings.map_name

    if map_name == "real" or map_name == "map_a" or "real" in map_name or map_name == "map-a":
        map_name = MAP_A
        logging.info(f"Map A with name {map_name}")

    elif map_name == "fictitious" or map_name == "map_b" or "fictitious" in map_name or map_name == "map-b":
        map_name = MAP_B
        logging.info(f"Map B with name {map_name}")

    else:
        map_name = MAP_A
        logging.info(f"Map name provided incorrectly, default to Map A with name {map_name}")

    return map_name, redis_inventory_key


@app.get("/db")
def index():
    get_database("rossini", redis_client)
    return {"message": "connected"}


@app.get("/db1")
def index_db1():
    db, _ = get_database("rossini", redis_client)
    collection = db["components"]

    data = {}
    items = collection.find()
    for item in items:
        data[item["name"]] = {"1"}

    return data


@app.get("/rossini_api")
def index_rossini_api():
    try:
        response = requests_retry_session().get(
            f'http://{settings.ip_address}:{settings.port}',
            timeout=5
        )

    except Exception as e:
        logging.error(e.__class__.__name__, exc_info=True)
        return {"message": e.__class__.__name__}

    else:
        logging.info(response.status_code, exc_info=True)
        return {"message": response.status_code}


async def _calculate_risks(sensor_input: dict):
    # get map name
    sensor_input["map_name"], redis_inventory_key = _get_map_name(sensor_input["map_name"])

    # Run risk calculations
    risk = Risk(sensor_input, redis_inventory_key, redis_client)

    if risk.inventory_cache_exists:
        risk.compute_risks_from_cached_db()
        risk.combine_structural_risks_with_cached()

    else:
        risk.compute_risks()
        risk.combine_structural_risks_with_cached()

        # Cache
        cache_data("inventory_" + redis_inventory_key, json_util.dumps(risk.inventory_cache), seconds=86400)

    return risk.risks, risk.indices_structure


@app.put("/risks")
async def put_risks(sensor_input: SensorInput1):

    sensor_input = sensor_input.dict()

    # Structural risk
    structural_risk, indices_structure = await _calculate_risks(sensor_input)

    # Cache
    cache_data("structural_risk", structural_risk, seconds=3600)

    # Ambiental risk
    ambiental_risk = sensor_input["ambiental_risk"]

    logging.info("Length of structural risk values %s", len(structural_risk))

    if ambiental_risk is not None and len(structural_risk) != len(ambiental_risk):
        raise ValueError(f"Risk lengths do not match, environmental: {len(ambiental_risk)}, "
                         f"structural: {len(structural_risk)}")

    if ambiental_risk is not None:

        cache_data("ambiental_risk", ambiental_risk, seconds=3600)

        for idx in indices_structure:
            ambiental_risk[idx] = 0

        logging.info("Length of environmental risk values %s", len(ambiental_risk))
        response = update_risks(structural_risk, ambiental_risk)
        return response[0]

    logging.info("Environmental risks missing")

    response = update_risks(structural_risk, structural_risk)

    return response[0]
