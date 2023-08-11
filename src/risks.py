"""
maps and coordinate system
reference-point of (0, 0) refers to top left white pixel
Coordinates of Rossini component database are set with respect to reference-point in cm.

Normalizes coordinates of all components
and assigns cell IDs
"""
from pathlib import Path
import math
from typing import List
import logging
import json
import numpy as np
import re
import yaml
from scipy import stats
from scipy.interpolate import interp1d
import redis

from .get_sat import get_sat
from src.utils import read_map, requests_retry_session
from src.get_db import connect_to_dabase
from src.config import settings

# todo, update to connect to Maps on a server
PATH = Path(__file__).resolve().parent
PATH_MAPS = PATH.parents[0] / "maps"


def update_risks(structural: List[int], ambiental: List[int]):
    combined = [*map(max, zip(structural, ambiental))]

    headers = {
        'Content-Type': 'application/json',
    }

    out = {"personal_protection_equipment": "placeholder",
           "map": [
               {"floor": 0,
                "risk_values": combined},
               {"floor": 1,
                "risk_values": [0]}
           ]}

    try:
        response = requests_retry_session().put(
            f'http://{settings.ip_address}:{settings.port}/map',
            timeout=5,
            headers=headers,
            data=json.dumps(out),
        )

    except Exception as e:
        logging.error(e.__class__.__name__, exc_info=True)
        return {"message": e.__class__.__name__}

    else:
        logging.info(response.status_code, exc_info=True)
        return out, response


class Risk:
    # Risk immediate area: influence_risk
    RISK_MAP = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 1,
        5: 2,
        6: 3,
        7: 4,
        8: 5,
        9: 6,
    }

    STRUCTURE_IDS = {
        "622204f35ed4ed1b0bb72c18", 
        "622204ff5ed4ed1b0bb72c1a", 
        "6222051d5ed4ed1b0bb72c1c",
        "622205335ed4ed1b0bb72c1e",
    }

    # Map name: cell_Id, x in px, y in px
    REFERENCE = {
        "2-Navigation_map_v1.0": {
            "cell_id": 3227,
            "h": 26.0,
            "v": 24.0,
        },
        "2-NavigationFile": {
            "cell_id": 5895,
            "h": 8.5,
            "v": 8.5,
        }
    }

    RISK_0 = 0.04
    RISK_INTERVAL = 0.16
    PGA_RANGE = np.linspace(0.01, 10.0, 200)

    inventory_cache = dict()

    def __init__(self, sensor_input: dict, redis_inventory_key: str, client: redis.Redis = None):
        """Risk mapping

        Parameters
        ----------
        sensor_input : dict
                Acceleration time history in [g]
                Time history time step in [s]
                Map name as string
        redis_inventory_key : str
                Redis inventory key
        client : redis.Redis, optional
                Redis Client, by default None
        """
        
        self._get_constants()
        
        self.client = client
        self.db, self.inventory_cache_exists = connect_to_dabase(
            settings.database_name, redis_inventory_key, client=client)
        self.redis_inventory_key = "inventory_" + redis_inventory_key
        self.map_name = sensor_input["map_name"]
        self.grid = read_map(PATH_MAPS, self.map_name)
        self.scene_name = self.grid["scene_name"]

        # Coordinates of center of cell 0 with respect to (0, 0) = first white pixel
        self.ref_v, self.ref_h = self._identify_cell_0_position()

        # Risk arrays
        self.risks = self._init_risk_arrays()

        self.sensor_input = sensor_input

        # Indexes of structural components
        self.indices_structure = set()

        # Sensors
        try:
            self.sensors = self.sensor_input["sensors"]
        except KeyError:
            self.sensors = None

    def _get_constants(self):
        
        with open(PATH / "constants.yaml", "r") as f:
            constants = yaml.safe_load(f)
        
        self.STRUCTURE_IDS = constants.get('STRUCTURE_IDS', self.STRUCTURE_IDS)
        if self.STRUCTURE_IDS is not None:
            self.STRUCTURE_IDS = set(self.STRUCTURE_IDS)

        self.REFERENCE = constants.get('REFERENCE', self.REFERENCE)
        self.RISK_MAP = constants.get('RISK_MAP', self.RISK_MAP)

    def _init_risk_arrays(self):
        rows = self.grid["rows"]
        columns = self.grid["columns"]
        cell_count = rows * columns

        return np.zeros(cell_count, dtype=int)

    def _identify_cell_0_position(self):
        ref_cell_id = self.REFERENCE[self.map_name]["cell_id"]
        ref_h = self.REFERENCE[self.map_name]["h"] * \
            self.grid["millimeter_per_pixel"] / 10
        ref_v = self.REFERENCE[self.map_name]["v"] * \
            self.grid["millimeter_per_pixel"] / 10

        columns = self.grid["columns"]

        # Coordinates of center of cell 0 with respect to (0, 0) = first white pixel
        up = ref_v - ref_cell_id // columns * \
            self.grid["cell_size_cm"] - self.grid["cell_size_cm"] / 2
        left = ref_h - ref_cell_id % columns * \
            self.grid["cell_size_cm"] - self.grid["cell_size_cm"] / 2

        return up, left

    def _get_cell_id(self, location):
        columns = self.grid["columns"]
        cell_size = self.grid["cell_size_cm"]

        cells = set()
        influence_cells = set()

        topLeft = location["topLeft"]
        bottomRight = location["bottomRight"]
        influenceRadius = location["influenceRadius"]

        # X range, start is included, end is not included
        x_start = math.floor(round(topLeft[0] - self.ref_h, 0) / cell_size)
        x_end = math.ceil(round(bottomRight[0] - self.ref_h, 0) / cell_size)
        # Y range
        y_start = math.floor(round(topLeft[1] - self.ref_v, 0) / cell_size)
        y_end = math.ceil(round(bottomRight[1] - self.ref_v, 0) / cell_size)

        for i in range(y_start, y_end):
            for j in range(x_start, x_end):
                cells.add(i * columns + j)
        for i in range(y_start, y_end):
            for j in range(x_start, x_end):
                cells.add(i * columns + j)

        # Influence zone
        x_start = max(0, math.floor(
            round(topLeft[0] - influenceRadius - self.ref_h, 0) / cell_size))
        x_end = math.ceil(
            round(bottomRight[0] + influenceRadius - self.ref_h, 0) / cell_size)
        y_start = max(0, math.floor(
            round(topLeft[1] - influenceRadius - self.ref_v, 0) / cell_size))
        y_end = math.ceil(
            round(bottomRight[1] + influenceRadius - self.ref_v, 0) / cell_size)

        for i in range(y_start, y_end):
            for j in range(x_start, x_end):
                cell_id = i * columns + j
                if cell_id in cells:
                    continue

                influence_cells.add(cell_id)

        return list(cells), list(influence_cells), [topLeft, bottomRight]

    def compute_earthquake_intensity(self, period, damping, position):
        if self.sensors is None:
            return 0
        if len(self.sensors) == 1:
            # A single sensor was provided
            return get_sat(self.sensors[0]["data"][0], self.sensors[0]["data"][1], period, damping)

        # Multiple sensors were provided
        n_sensors = len(self.sensors)
        x = np.zeros(n_sensors)
        y = np.zeros(n_sensors)

        for i in range(n_sensors):
            sensor_location = self.sensors[i]["location"]
            x[i], y[i] = sensor_location

        # Centroid of a rectangular component
        center_h = (position[0][0] + position[1][0]) / 2
        center_v = (position[0][1] + position[1][1]) / 2

        distance = np.sqrt((center_h - x) ** 2 + (center_v - y) ** 2)
        distance_index = np.argmin(distance)
        sensor_data = self.sensors[distance_index]

        return get_sat(sensor_data["data"][0], sensor_data["data"][1], period, damping)

    def derive_fragility(self, damage_state, fragility, position):
        # Fragility function information, Period and Damping
        imName = fragility["imName"]

        if imName.lower() == "pga":
            period = 0.0
            damping = 0.02
        else:
            imName = re.findall(r"\d+(?:\.\d+)?", imName)

            period = float(imName[0])
            damping = float(imName[1]) / 100

        # Critical damage state
        ds = damage_state[0]
        mean = ds["mean"]
        dispersion = ds["dispersion"]

        if mean == 0:
            return 0

        probabilities = stats.norm.cdf(
            np.log(self.PGA_RANGE / mean) / dispersion, loc=0, scale=1)
        interpolation = interp1d(self.PGA_RANGE, probabilities)

        # Get intensity level
        intensity = self.compute_earthquake_intensity(
            period, damping, position)

        if intensity > max(self.PGA_RANGE):
            return 9
        if intensity == 0 or intensity < min(self.PGA_RANGE):
            return 0

        p = interpolation(intensity)
        if p - self.RISK_0 < 0:
            return 0

        return math.ceil((p - self.RISK_0) / self.RISK_INTERVAL) + 3

    def compute_risks_from_cached_db(self):
        collection = json.loads(self.db[self.redis_inventory_key])

        for item in collection:
            # Get fragility data
            damage_state = collection[item]["damages"]
            fragility = collection[item]["fragilities"]

            # Get locations
            locations = collection[item]["locations"]

            for location in locations:
                cells, influence_cells, exact_position = self._get_cell_id(
                    location)

                # Append into structure's indices
                if str(item) in self.STRUCTURE_IDS:
                    self.indices_structure.update(cells)

                # Compute risk
                risk_level = self.derive_fragility(
                    damage_state, fragility, exact_position)

                # Get cell IDs
                cells = np.intersect1d(
                    cells, np.where(self.risks < risk_level))
                if len(cells) > 0:
                    self.risks[cells] = risk_level

                # Risk at influence zone
                influence_risk = max(0, risk_level - 3)
                cells = np.intersect1d(
                    influence_cells, np.where(self.risks < influence_risk))
                if len(cells) > 0:
                    self.risks[cells] = influence_risk

    def compute_risks(self):
        collection = self.db["components"]
        damage_states = self.db["damages"]
        fragilities = self.db["fragilities"]

        if bool(re.match('real', self.scene_name, re.I)):
            coordinates = self.db["realcoordinates"]
        else:
            coordinates = self.db["coordinates"]

        # All components
        items = collection.find({}, {"_id": 1})

        # For each component
        for item in items:
            locations = list(coordinates.find({"component": item["_id"]}))

            if not locations:
                continue

            item_id = str(item["_id"])

            # Get fragility data
            damage_state = list(damage_states.find({"component": item["_id"]}, {"mean": 1, "dispersion": 1})
                                .sort("mean", -1).limit(1))
            fragility = fragilities.find_one({"component": item["_id"]})

            # Caching
            self.inventory_cache[item_id] = {
                "locations": locations,
                "damages": damage_state,
                "fragilities": fragility,
            }

            # If location exists, loop over each location
            for location in locations:
                cells, influence_cells, exact_position = self._get_cell_id(
                    location)

                # Append into structure's indices
                if item_id in self.STRUCTURE_IDS:
                    self.indices_structure.update(cells)

                # Calculate risk
                risk_level = self.derive_fragility(
                    damage_state, fragility, exact_position)

                # Get cell IDs
                cells = np.intersect1d(
                    cells, np.where(self.risks < risk_level))
                if len(cells) > 0:
                    self.risks[cells] = risk_level

                # Risk at influence zone
                influence_risk = max(0, risk_level - 3)
                cells = np.intersect1d(
                    influence_cells, np.where(self.risks < influence_risk))
                if len(cells) > 0:
                    self.risks[cells] = influence_risk

    def combine_structural_risks_with_cached(self):

        self.risks = self.risks.tolist()

        risk_cache = self.client.get("structural_risk")
        if risk_cache is not None:
            logging.info("Combining with cached structural risk")

            structural_risk_cache = json.loads(risk_cache)['structural_risk']
            self.risks = list(map(max, zip(self.risks, structural_risk_cache)))
