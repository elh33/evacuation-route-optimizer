import geopandas as gpd
import pandas as pd
import os
from typing import Dict, List, Any
from shapely.geometry import Point

class DataSynchronizer:
    """
    Class to synchronize various data sources for evacuation planning.
    Merges hazard, weather, and traffic data into a single GeoDataFrame.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the DataSynchronizer with data directory path.

        Args:
            data_dir: Path to the directory containing data files
        """
        self.data_dir = data_dir
        self.hazard_gdf = None
        self.weather_gdf = None
        self.traffic_gdf = None
        self.synchronized_gdf = None

    def load_data(self) -> None:
        """Load hazard, weather and traffic data from files."""
        # Define file paths
        hazard_file = os.path.join(self.data_dir, "hazards_processed.geojson")
        weather_file = os.path.join(self.data_dir, "weather_processed.geojson")
        traffic_file = os.path.join(self.data_dir, "traffic_processed.geojson")

        # Load data if files exist
        if os.path.exists(hazard_file):
            self.hazard_gdf = gpd.read_file(hazard_file)
            print(f"Loaded {len(self.hazard_gdf)} hazard records")
        else:
            self.hazard_gdf = gpd.GeoDataFrame(columns=['id', 'type', 'severity', 'geometry'])
            print("Hazard file not found, created empty DataFrame")

        if os.path.exists(weather_file):
            self.weather_gdf = gpd.read_file(weather_file)
            print(f"Loaded {len(self.weather_gdf)} weather records")
        else:
            self.weather_gdf = gpd.GeoDataFrame(columns=['id', 'temperature', 'precipitation', 'wind_speed', 'geometry'])
            print("Weather file not found, created empty DataFrame")

        if os.path.exists(traffic_file):
            self.traffic_gdf = gpd.read_file(traffic_file)
            print(f"Loaded {len(self.traffic_gdf)} traffic records")
        else:
            self.traffic_gdf = gpd.GeoDataFrame(columns=['id', 'density', 'timestamp', 'geometry'])
            print("Traffic file not found, created empty DataFrame")

    def merge_all_layers(self) -> None:
        """Merge all data layers into a single synchronized GeoDataFrame."""
        if not all([self.hazard_gdf is not None,
                   self.weather_gdf is not None,
                   self.traffic_gdf is not None]):
            raise ValueError("Data layers must be loaded before merging")

        # Create a spatial join of all data layers
        # First standardize CRS if needed
        crs = "EPSG:4326"  # WGS84

        if self.hazard_gdf.crs != crs:
            self.hazard_gdf = self.hazard_gdf.to_crs(crs)

        if self.weather_gdf.crs != crs:
            self.weather_gdf = self.weather_gdf.to_crs(crs)

        if self.traffic_gdf.crs != crs:
            self.traffic_gdf = self.traffic_gdf.to_crs(crs)

        # Start with hazard data and join others
        # First create a buffer around points to allow for spatial joins
        hazard_buffered = self.hazard_gdf.copy()
        hazard_buffered['geometry'] = hazard_buffered.geometry.buffer(0.01)  # ~1km buffer

        # Join weather data to hazard data based on proximity
        merged = gpd.sjoin_nearest(
            hazard_buffered,
            self.weather_gdf,
            how="left",
            distance_col="dist_to_weather"
        )

        # Rename columns to avoid conflicts
        merged = merged.rename(columns={
            'id_left': 'hazard_id',
            'id_right': 'weather_id',
            'type': 'hazard_type',
            'severity': 'hazard_severity'
        })

        # Join traffic data
        merged = gpd.sjoin_nearest(
            merged,
            self.traffic_gdf,
            how="left",
            distance_col="dist_to_traffic"
        )

        # Rename traffic columns
        merged = merged.rename(columns={
            'id': 'traffic_id',
            'density': 'traffic_density',
            'timestamp': 'traffic_timestamp'
        })

        # Clean up and format the results
        self.synchronized_gdf = merged.drop(columns=['index_right'])

        # Calculate a combined risk score (example formula)
        self.synchronized_gdf['risk_score'] = (
            self.synchronized_gdf['hazard_severity'].fillna(0) * 0.6 +
            self.synchronized_gdf['traffic_density'].fillna(0) / 100 * 0.3 +
            (self.synchronized_gdf['precipitation'].fillna(0) / 10) * 0.1
        )

        print(f"Synchronized data contains {len(self.synchronized_gdf)} records")

    def export(self, output_file: str = None) -> None:
        """
        Export the synchronized data to a GeoJSON file.

        Args:
            output_file: Path to the output file. If None, uses default path.
        """
        if self.synchronized_gdf is None:
            raise ValueError("No synchronized data to export")

        if output_file is None:
            output_file = os.path.join(self.data_dir, "synchronized_data.geojson")

        # Make sure the directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Export to GeoJSON
        self.synchronized_gdf.to_file(output_file, driver="GeoJSON")
        print(f"Exported synchronized data to {output_file}")

    def get_data_as_dict(self) -> List[Dict[str, Any]]:
        """Retourne les données synchronisées sous forme dict pour usage programmatique (ex: dashboard)"""
        return self.synchronized_gdf.to_dict("records")

# Exemple d'utilisation
if __name__ == "__main__":
    sync = DataSynchronizer()
    sync.load_data()
    sync.merge_all_layers()
    sync.export()