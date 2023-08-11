from pydantic import BaseModel, root_validator, validator
from typing import List


class Floor(BaseModel):
    floor: int
    risk_values: List[int]


class RiskOut(BaseModel):
    personal_protection_equipment: str
    map: List[Floor]


class SensorData(BaseModel):
    name: str = None
    accelerations: List[float]
    time_step: float


class SensorInput(BaseModel):
    sensors: List[SensorData]
    x: List[float] = None
    y: List[float] = None
    ambiental_risk: List[float] = None

    @root_validator(pre=True)
    def validate_length(cls, values):
        s, x, y = values.get("sensors"), values.get("x"), values.get("y")

        if len(s) > 1 and (x is None or y is None):
            raise ValueError("multiple sensors provided, coordinates are missing")

        if len(s) > 1 and not(len(s) == len(x) == len(y)):
            raise ValueError("number of sensors does not match number of coordinates provides")
        return values

    @validator('sensors', pre=True)
    def is_sensors_empty(cls, v):
        if len(v) < 1:
            raise ValueError("Sensor data is missing")
        return v


class SensorData1(BaseModel):
    name: str = None
    type: str = None
    # [acceleration series, time series]
    data: List[List[float]]
    location: tuple = None


class SensorInput1(BaseModel):
    sensors: List[SensorData1] = None
    ambiental_risk: List[int] = None
    map_name: str = None
