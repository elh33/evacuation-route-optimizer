from pydantic import BaseModel
from typing import List, Optional

class Coordinates(BaseModel):
    lon: float
    lat: float

class HazardPoint(BaseModel):
    id: Optional[int]
    type: str
    description: Optional[str]
    location: Coordinates

class WeatherPoint(BaseModel):
    id: Optional[int]
    temperature: float
    precipitation: Optional[float]
    wind_speed: Optional[float]
    location: Coordinates

class TrafficPoint(BaseModel):
    id: Optional[int]
    density: int
    timestamp: Optional[str]
    location: Coordinates
