import os
import json
import requests
from datetime import datetime
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from dotenv import load_dotenv

class WeatherCollector:
    """Collects weather data from OpenWeatherMap API and processes it for evacuation planning."""

    def __init__(self, api_key=None, output_dir="data/raw/weather"):
        """
        Initialize the weather collector.

        Args:
            api_key: OpenWeatherMap API key (optional, will use env variable if not provided)
            output_dir: Directory to save collected weather data
        """
        # Load environment variables
        load_dotenv()

        # Get API key from parameters or environment variables
        self.api_key = api_key or os.getenv("OPENWEATHERMAP_API_KEY")
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key is required")

        # Create output directory if it doesn't exist
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # API endpoints
        self.current_weather_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    def fetch_current_weather(self, city):
        """
        Fetch current weather data for a city.

        Args:
            city: City name (e.g., "Paris,FR")

        Returns:
            JSON response from the API
        """
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }

        response = requests.get(self.current_weather_url, params=params)
        response.raise_for_status()
        return response.json()

    def fetch_forecast(self, city):
        """
        Fetch 5-day weather forecast for a city.

        Args:
            city: City name (e.g., "Paris,FR")

        Returns:
            JSON response from the API
        """
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }

        response = requests.get(self.forecast_url, params=params)
        response.raise_for_status()
        return response.json()

    def process_weather_data(self, current_data, forecast_data):
        """
        Process current weather and forecast data into a GeoDataFrame.

        Args:
            current_data: Current weather JSON data
            forecast_data: Forecast JSON data

        Returns:
            GeoDataFrame with processed weather data
        """
        # Process current weather
        current_entry = {
            "timestamp": datetime.utcfromtimestamp(current_data["dt"]).isoformat(),
            "city": current_data["name"],
            "temperature": current_data["main"]["temp"],
            "pressure": current_data["main"]["pressure"],
            "humidity": current_data["main"]["humidity"],
            "wind_speed": current_data["wind"]["speed"],
            "wind_direction": current_data.get("wind", {}).get("deg", 0),
            "weather_main": current_data["weather"][0]["main"],
            "weather_description": current_data["weather"][0]["description"],
            "rain_1h": current_data.get("rain", {}).get("1h", 0),
            "clouds": current_data["clouds"]["all"],
            "lon": current_data["coord"]["lon"],
            "lat": current_data["coord"]["lat"],
            "forecast_type": "current"
        }

        # Process forecast data
        forecast_entries = []
        for forecast in forecast_data["list"]:
            entry = {
                "timestamp": datetime.utcfromtimestamp(forecast["dt"]).isoformat(),
                "city": forecast_data["city"]["name"],
                "temperature": forecast["main"]["temp"],
                "pressure": forecast["main"]["pressure"],
                "humidity": forecast["main"]["humidity"],
                "wind_speed": forecast["wind"]["speed"],
                "wind_direction": forecast["wind"]["deg"],
                "weather_main": forecast["weather"][0]["main"],
                "weather_description": forecast["weather"][0]["description"],
                "rain_3h": forecast.get("rain", {}).get("3h", 0),
                "clouds": forecast["clouds"]["all"],
                "lon": forecast_data["city"]["coord"]["lon"],
                "lat": forecast_data["city"]["coord"]["lat"],
                "forecast_type": "forecast"
            }
            forecast_entries.append(entry)

        # Combine current and forecast data
        all_entries = [current_entry] + forecast_entries

        # Create DataFrame
        df = pd.DataFrame(all_entries)

        # Create geometry column
        geometry = [Point(lon, lat) for lon, lat in zip(df["lon"], df["lat"])]

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

        return gdf

    def calculate_weather_risk(self, gdf):
        """
        Calculate risk levels based on weather conditions.

        Args:
            gdf: GeoDataFrame with weather data

        Returns:
            GeoDataFrame with added risk levels
        """
        # Calculate risk factors (simplified)

        # Heavy rain risk (0-1)
        gdf["rain_risk"] = gdf["rain_3h"].fillna(gdf["rain_1h"]).fillna(0) / 10
        gdf["rain_risk"] = gdf["rain_risk"].clip(0, 1)

        # Wind risk (0-1)
        gdf["wind_risk"] = gdf["wind_speed"] / 30  # Assuming 30 m/s is max risk
        gdf["wind_risk"] = gdf["wind_risk"].clip(0, 1)

        # Extreme temperature risk
        gdf["temp_risk"] = 0.0
        # High temperature risk
        gdf.loc[gdf["temperature"] > 35, "temp_risk"] = (gdf["temperature"] - 35) / 15
        # Low temperature risk
        gdf.loc[gdf["temperature"] < 0, "temp_risk"] = abs(gdf["temperature"]) / 20
        gdf["temp_risk"] = gdf["temp_risk"].clip(0, 1)

        # Weather type risk (categorical)
        risk_mapping = {
            "Clear": 0.0,
            "Clouds": 0.1,
            "Drizzle": 0.3,
            "Rain": 0.5,
            "Thunderstorm": 0.8,
            "Snow": 0.6,
            "Mist": 0.4,
            "Fog": 0.6,
            "Tornado": 1.0,
            "Hurricane": 1.0
        }
        gdf["weather_risk"] = gdf["weather_main"].map(risk_mapping).fillna(0.5)

        # Total weather risk (weighted sum)
        gdf["total_risk"] = (
            0.4 * gdf["rain_risk"] +
            0.3 * gdf["wind_risk"] +
            0.1 * gdf["temp_risk"] +
            0.2 * gdf["weather_risk"]
        )

        return gdf

    def collect_and_process(self, city):
        """
        Collect and process weather data for a city.

        Args:
            city: City name (e.g., "Paris,FR")

        Returns:
            Processed GeoDataFrame with weather data and risk levels
        """
        try:
            # Fetch data
            current_data = self.fetch_current_weather(city)
            forecast_data = self.fetch_forecast(city)

            # Process data
            weather_gdf = self.process_weather_data(current_data, forecast_data)

            # Calculate risk levels
            weather_gdf = self.calculate_weather_risk(weather_gdf)

            # Save raw data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_file = os.path.join(self.output_dir, f"current_{city.replace(',', '_')}_{timestamp}.json")
            forecast_file = os.path.join(self.output_dir, f"forecast_{city.replace(',', '_')}_{timestamp}.json")
            processed_file = os.path.join(self.output_dir, f"weather_{city.replace(',', '_')}_{timestamp}.geojson")

            with open(current_file, "w") as f:
                json.dump(current_data, f, indent=2)

            with open(forecast_file, "w") as f:
                json.dump(forecast_data, f, indent=2)

            # Save processed GeoDataFrame
            weather_gdf.to_file(processed_file, driver="GeoJSON")

            return weather_gdf

        except Exception as e:
            print(f"Error collecting weather data for {city}: {e}")
            return None

# Example usage
if __name__ == "__main__":
    collector = WeatherCollector()
    city = "Paris,FR"
    weather_gdf = collector.collect_and_process(city)

    if weather_gdf is not None:
        print(f"Successfully collected weather data for {city}")
        print(f"Number of records: {len(weather_gdf)}")
        print(f"Columns: {weather_gdf.columns.tolist()}")
        print(f"Sample data:")
        print(weather_gdf[["timestamp", "temperature", "weather_main", "total_risk"]].head())