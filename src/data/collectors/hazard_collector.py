import os
import requests
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from shapely.geometry import Point, Polygon

class HazardCollector:
    """
    Collects hazard data from various sources and combines them for evacuation route planning.

    This class handles collection of data about various hazards like floods, fires, chemical spills,
    or any other dangerous situations that might affect evacuation routes.
    """

    def __init__(self, data_dir: str = "data", api_key: Optional[str] = None):
        """
        Initialize the hazard collector with configuration.

        Args:
            data_dir: Directory to store downloaded and processed hazard data
            api_key: API key for external hazard data services (if needed)
        """
        self.data_dir = Path(data_dir)
        self.raw_data_dir = self.data_dir / "raw" / "hazard_maps"
        self.processed_data_dir = self.data_dir / "processed"
        self.api_key = api_key

        # Ensure directories exist
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def collect_hazard_data(self, city: str, bbox: Optional[List[float]] = None) -> pd.DataFrame:
        """
        Collect hazard data for a specific city or bounding box.

        Args:
            city: Name of the city to collect data for
            bbox: Optional bounding box [min_lon, min_lat, max_lon, max_lat]

        Returns:
            DataFrame containing collected hazard data
        """
        self.logger.info(f"Collecting hazard data for: {city}")

        # Try to collect data from various sources
        hazards = []

        # 1. Try to collect from official APIs
        official_hazards = self._collect_from_official_sources(city, bbox)
        if official_hazards:
            hazards.extend(official_hazards)

        # 2. Try to collect historical hazard data
        historical_hazards = self._collect_historical_data(city, bbox)
        if historical_hazards:
            hazards.extend(historical_hazards)

        # 3. If no data available, generate simulated data
        if len(hazards) == 0:
            self.logger.warning(f"No real hazard data available for {city}, using simulated data")
            simulated_hazards = self._generate_simulated_hazards(city, bbox)
            hazards.extend(simulated_hazards)

        # Create DataFrame from the collected hazards
        hazard_df = pd.DataFrame(hazards)

        # Save raw data
        raw_file_path = self.raw_data_dir / f"{city.lower()}_hazards_raw.csv"
        hazard_df.to_csv(raw_file_path, index=False)
        self.logger.info(f"Raw hazard data saved to {raw_file_path}")

        return hazard_df

    def _collect_from_official_sources(self, city: str, bbox: Optional[List[float]]) -> List[Dict]:
        """
        Collect hazard data from official sources like government agencies.

        Args:
            city: Name of the city
            bbox: Bounding box for the area

        Returns:
            List of hazard records
        """
        hazards = []

        # This would be implemented to call actual APIs
        # For example, national weather service for floods, fire departments for fires, etc.
        # Example implementation:

        try:
            # This is a placeholder - in a real implementation this would use actual API endpoints
            if self.api_key:
                # Example API call to a hypothetical hazard API
                # response = requests.get(f"https://api.hazards.example/v1/{city}?api_key={self.api_key}")
                # if response.status_code == 200:
                #     for record in response.json().get("hazards", []):
                #         hazards.append({
                #             "type": record["hazard_type"],
                #             "severity": record["severity"],
                #             "latitude": record["lat"],
                #             "longitude": record["lon"],
                #             "description": record["description"],
                #             "timestamp": record["time"],
                #             "source": "official_api"
                #         })
                pass
        except Exception as e:
            self.logger.error(f"Error collecting official hazard data: {e}")

        return hazards

    def _collect_historical_data(self, city: str, bbox: Optional[List[float]]) -> List[Dict]:
        """
        Collect historical hazard data for the area to identify common hazard zones.

        Args:
            city: Name of the city
            bbox: Bounding box for the area

        Returns:
            List of hazard records
        """
        hazards = []

        # This would look for historical data files or databases
        history_file = self.raw_data_dir / f"{city.lower()}_hazards_history.csv"

        if history_file.exists():
            try:
                history_df = pd.read_csv(history_file)
                for _, row in history_df.iterrows():
                    hazards.append({
                        "type": row.get("type", "unknown"),
                        "severity": row.get("severity", 0.5),
                        "latitude": row.get("latitude"),
                        "longitude": row.get("longitude"),
                        "description": row.get("description", "Historical hazard zone"),
                        "timestamp": datetime.now().isoformat(),
                        "source": "historical_data"
                    })
            except Exception as e:
                self.logger.error(f"Error reading historical data: {e}")

        return hazards

    def _generate_simulated_hazards(self, city: str, bbox: Optional[List[float]]) -> List[Dict]:
        """
        Generate simulated hazard data when no real data is available.

        Args:
            city: Name of the city
            bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]

        Returns:
            List of simulated hazard records
        """
        hazards = []

        # Use default bbox if none provided
        if bbox is None:
            # Default to a generic area as placeholder
            bbox = [-0.1, 51.4, 0.1, 51.6]  # Example for London

        min_lon, min_lat, max_lon, max_lat = bbox

        # Generate a few random hazards of different types
        hazard_types = ["flood", "fire", "chemical_spill", "landslide", "storm"]

        # Number of hazards to generate
        num_hazards = np.random.randint(3, 8)

        for _ in range(num_hazards):
            hazard_type = np.random.choice(hazard_types)

            # Generate location within bbox
            lat = np.random.uniform(min_lat, max_lat)
            lon = np.random.uniform(min_lon, max_lon)

            # Generate severity level (0 to 1)
            severity = round(np.random.uniform(0.3, 0.9), 2)

            # Generate radius or affected area size (in kilometers)
            radius = round(np.random.uniform(0.1, 1.0), 2)

            hazards.append({
                "type": hazard_type,
                "severity": severity,
                "latitude": lat,
                "longitude": lon,
                "radius_km": radius,
                "description": f"Simulated {hazard_type} hazard",
                "timestamp": datetime.now().isoformat(),
                "source": "simulation"
            })

        return hazards

    def process_hazard_data(self, hazard_df: pd.DataFrame) -> gpd.GeoDataFrame:
        """
        Process hazard data into a standardized GeoDataFrame.

        Args:
            hazard_df: DataFrame containing hazard data

        Returns:
            GeoDataFrame with hazard points and zones
        """
        self.logger.info("Processing hazard data")

        # Create a copy to avoid modifying the original
        df = hazard_df.copy()

        # Convert to GeoDataFrame
        geometry = [Point(row.longitude, row.latitude) for _, row in df.iterrows()]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

        # For hazards with radius, create polygon geometries
        hazard_polygons = []

        for idx, row in gdf.iterrows():
            if "radius_km" in row and row.radius_km > 0:
                # Convert radius from km to degrees (approximate)
                radius_degrees = row.radius_km / 111.0

                # Create a circle as polygon with 20 points
                circle = Point(row.longitude, row.latitude).buffer(radius_degrees, resolution=20)

                hazard_polygons.append({
                    "type": row.type,
                    "severity": row.severity,
                    "description": row.description,
                    "timestamp": row.timestamp,
                    "source": row.source,
                    "geometry": circle
                })

        # If we have polygon hazards, create a separate GeoDataFrame
        if hazard_polygons:
            polygon_gdf = gpd.GeoDataFrame(hazard_polygons, crs="EPSG:4326")

            # Combine point and polygon hazards
            gdf = pd.concat([gdf, polygon_gdf], ignore_index=True)

        # Add risk levels to be used in routing algorithms
        gdf["risk_level"] = gdf.severity.fillna(0.5)  # Default risk 0.5 if no severity

        return gdf

    def save_processed_data(self, gdf: gpd.GeoDataFrame, city: str) -> str:
        """
        Save processed hazard data to a GeoJSON file.

        Args:
            gdf: GeoDataFrame with processed hazard data
            city: City name to use in the filename

        Returns:
            Path to the saved file
        """
        self.logger.info("Saving processed hazard data")

        # Create filename
        file_path = self.processed_data_dir / f"{city.lower()}_hazards_processed.geojson"

        # Save as GeoJSON
        gdf.to_file(file_path, driver="GeoJSON")

        self.logger.info(f"Hazard data saved to {file_path}")
        return str(file_path)

    def run_collection_pipeline(self, city: str, bbox: Optional[List[float]] = None) -> gpd.GeoDataFrame:
        """
        Run the full hazard data collection and processing pipeline.

        Args:
            city: Name of the city to collect data for
            bbox: Optional bounding box [min_lon, min_lat, max_lon, max_lat]

        Returns:
            Processed GeoDataFrame with hazard data
        """
        # Collect data
        hazard_df = self.collect_hazard_data(city, bbox)

        # Process data
        hazard_gdf = self.process_hazard_data(hazard_df)

        # Save processed data
        self.save_processed_data(hazard_gdf, city)

        return hazard_gdf

# Example usage
if __name__ == "__main__":
    collector = HazardCollector()
    hazard_gdf = collector.run_collection_pipeline("Paris")
    print(f"Collected {len(hazard_gdf)} hazard records")