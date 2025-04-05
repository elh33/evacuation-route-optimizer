import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project directories
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SIMULATION_DATA_DIR = DATA_DIR / "simulation"
MODELS_DIR = BASE_DIR / "models"

# Create directories if they don't exist or fix if they're files
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, 
                SIMULATION_DATA_DIR, MODELS_DIR]:
    # If path exists but is a file, remove it and create directory
    if directory.exists() and not directory.is_dir():
        os.remove(directory)
    
    # Create directory (and parents)
    directory.mkdir(exist_ok=True, parents=True)

# Ensure raw data subdirectories exist
for subdir in ["osm", "weather", "hazard_maps", "traffic"]:
    dir_path = RAW_DATA_DIR / subdir
    if dir_path.exists() and not dir_path.is_dir():
        os.remove(dir_path)
    dir_path.mkdir(exist_ok=True)

# Ensure model subdirectories exist
for subdir in ["lstm", "gcn"]:
    dir_path = MODELS_DIR / subdir
    if dir_path.exists() and not dir_path.is_dir():
        os.remove(dir_path)
    dir_path.mkdir(exist_ok=True)

# API keys and credentials
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
OSM_API_KEY = os.getenv('OSM_API_KEY')

# Application settings
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')
DEFAULT_CITY = os.getenv('DEFAULT_CITY', 'Paris')
SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

# Pathfinding parameters
DEFAULT_RISK_WEIGHT = 0.7
DEFAULT_TIME_WEIGHT = 0.3