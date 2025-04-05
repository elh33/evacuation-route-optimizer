# Configuration settings for the evacuation route optimizer application

import os

class Config:
    # General settings
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    ENV = os.getenv('ENV', 'development')

    # Database settings
    DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///evacuation.db')

    # API settings
    API_KEY = os.getenv('API_KEY', 'your_api_key_here')

    # Paths
    DATA_DIR = os.getenv('DATA_DIR', 'data/')
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed/')
    RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw/')
    SIMULATION_DATA_DIR = os.path.join(DATA_DIR, 'simulation/')

    # Model settings
    LSTM_MODEL_PATH = os.getenv('LSTM_MODEL_PATH', 'models/lstm/')
    GCN_MODEL_PATH = os.getenv('GCN_MODEL_PATH', 'models/gcn/')

    # Other settings
    WEATHER_API_URL = os.getenv('WEATHER_API_URL', 'https://api.weather.com/')
    OSM_API_URL = os.getenv('OSM_API_URL', 'https://api.openstreetmap.org/')