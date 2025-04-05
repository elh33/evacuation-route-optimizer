"""Module for collecting weather data."""

import requests
import pandas as pd
import json
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

class WeatherCollector:
    """Class to collect and process weather data."""
    
    def __init__(self, data_dir: Path, api_key: str):
        """Initialize the weather collector.
        
        Args:
            data_dir: Directory where the weather data will be stored
            api_key: OpenWeatherMap API key
        """
        self.data_dir = data_dir
        self.weather_dir = data_dir / "raw" / "weather"
        self.weather_dir.mkdir(exist_ok=True, parents=True)
        self.api_key = api_key
        
    def get_current_weather(self, city_name: str) -> Dict[str, Any]:
        """Get current weather for a city.
        
        Args:
            city_name: Name of the city
            
        Returns:
            Dictionary with weather data
        """
        logging.info(f"Fetching current weather for {city_name}")
        
        try:
            # Make API request
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Extract relevant information
            weather_data = {
                'city': city_name,
                'timestamp': datetime.now().isoformat(),
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data.get('wind', {}).get('deg', 0),
                'precipitation': data.get('rain', {}).get('1h', 0) + data.get('snow', {}).get('1h', 0),
                'description': data['weather'][0]['description'],
                'conditions': data['weather'][0]['main'],
                'icon': data['weather'][0]['icon']
            }
            
            # Save to file
            self._save_weather_data(weather_data, city_name, 'current')
            
            return weather_data
            
        except Exception as e:
            logging.error(f"Error fetching weather for {city_name}: {str(e)}")
            # Return default data in case of error
            return {
                'city': city_name,
                'timestamp': datetime.now().isoformat(),
                'temperature': 20,
                'humidity': 70,
                'pressure': 1013,
                'wind_speed': 5,
                'wind_direction': 0,
                'precipitation': 0,
                'description': 'No data available',
                'conditions': 'Unknown',
                'icon': '01d'
            }
    
    def get_weather_forecast(self, city_name: str) -> List[Dict[str, Any]]:
        """Get weather forecast for a city.
        
        Args:
            city_name: Name of the city
            
        Returns:
            List of dictionaries with forecast data
        """
        logging.info(f"Fetching weather forecast for {city_name}")
        
        try:
            # Make API request
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Extract forecast data
            forecast_data = []
            
            for item in data['list']:
                forecast = {
                    'city': city_name,
                    'timestamp': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'wind_speed': item['wind']['speed'],
                    'wind_direction': item['wind'].get('deg', 0),
                    'precipitation': item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0),
                    'description': item['weather'][0]['description'],
                    'conditions': item['weather'][0]['main'],
                    'icon': item['weather'][0]['icon']
                }
                forecast_data.append(forecast)
            
            # Save to file
            self._save_weather_data({'forecast': forecast_data}, city_name, 'forecast')
            
            return forecast_data
            
        except Exception as e:
            logging.error(f"Error fetching forecast for {city_name}: {str(e)}")
            # Return default data in case of error
            return [
                {
                    'city': city_name,
                    'timestamp': (datetime.now() + timedelta(hours=i*3)).isoformat(),
                    'temperature': 20,
                    'humidity': 70,
                    'pressure': 1013,
                    'wind_speed': 5,
                    'wind_direction': 0,
                    'precipitation': 0,
                    'description': 'No data available',
                    'conditions': 'Unknown',
                    'icon': '01d'
                }
                for i in range(8)  # 24-hour forecast
            ]
    
    def _save_weather_data(self, data: Dict[str, Any], city_name: str, data_type: str) -> None:
        """Save weather data to disk.
        
        Args:
            data: Weather data dictionary
            city_name: Name of the city
            data_type: Type of data ('current' or 'forecast')
        """
        # Sanitize city name for file path
        city_file_name = city_name.replace(',', '').replace(' ', '_').lower()
        
        # Create a timestamp for the filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create the file path
        file_path = self.weather_dir / f"{city_file_name}_{data_type}_{timestamp}.json"
        
        try:
            # Save as JSON
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logging.info(f"Saved {data_type} weather data for {city_name} to {file_path}")
            
        except Exception as e:
            logging.error(f"Error saving weather data for {city_name}: {str(e)}")