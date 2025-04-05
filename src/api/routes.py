from fastapi import APIRouter
from fastapi.responses import JSONResponse
import geopandas as gpd
import os

router = APIRouter()

DATA_DIR = "data"
SYNCHRONIZED_FILE = os.path.join(DATA_DIR, "synchronized_data.geojson")

@router.get("/ping")
async def ping():
    return {"message": "API up and running!"}

@router.get("/synchronized-data")
async def get_synchronized_data():
    if not os.path.exists(SYNCHRONIZED_FILE):
        return JSONResponse(status_code=404, content={"error": "Data not found"})

    gdf = gpd.read_file(SYNCHRONIZED_FILE)
    return JSONResponse(content=gdf.to_json())

@router.get("/hazards")
async def get_hazards():
    file_path = os.path.join(DATA_DIR, "hazards_processed.geojson")
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "Hazard data not found"})

    gdf = gpd.read_file(file_path)
    return JSONResponse(content=gdf.to_json())

@router.get("/weather")
async def get_weather():
    file_path = os.path.join(DATA_DIR, "weather_processed.geojson")
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "Weather data not found"})

    gdf = gpd.read_file(file_path)
    return JSONResponse(content=gdf.to_json())

@router.get("/traffic")
async def get_traffic():
    file_path = os.path.join(DATA_DIR, "traffic_processed.geojson")
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "Traffic data not found"})

    gdf = gpd.read_file(file_path)
    return JSONResponse(content=gdf.to_json())
