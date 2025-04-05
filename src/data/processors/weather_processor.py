import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import json
import datetime

class WeatherProcessor:
    def __init__(self, input_path="data/weather_raw.geojson", output_path="data/weather_processed.geojson"):
        self.input_path = input_path
        self.output_path = output_path
        self.gdf = None

    def load_data(self):
        """Charge les données météo (GeoJSON)"""
        print(f"[INFO] Loading weather data from {self.input_path}")
        self.gdf = gpd.read_file(self.input_path)
        print(f"[INFO] Loaded {len(self.gdf)} weather observations.")

    def preprocess_data(self):
        """Nettoie et standardise les données météo"""
        if self.gdf is None:
            raise ValueError("Data not loaded.")

        print("[INFO] Preprocessing weather data...")

        self.gdf["timestamp"] = pd.to_datetime(self.gdf.get("timestamp", datetime.datetime.utcnow()))
        self.gdf["wind_speed"] = pd.to_numeric(self.gdf.get("wind_speed", 0), errors='coerce')
        self.gdf["rain_mm"] = pd.to_numeric(self.gdf.get("rain_mm", 0), errors='coerce')
        self.gdf["temperature"] = pd.to_numeric(self.gdf.get("temperature", 25), errors='coerce')

        # Normalisation
        self.gdf["wind_speed"] = self.gdf["wind_speed"].fillna(0)
        self.gdf["rain_mm"] = self.gdf["rain_mm"].fillna(0)

        print(f"[INFO] Preprocessed {len(self.gdf)} weather points.")

    def classify_risk(self, wind_threshold=50, rain_threshold=20):
        """Ajoute des colonnes pour identifier les zones à risque météo"""
        print("[INFO] Classifying weather risk zones...")

        self.gdf["is_storm"] = self.gdf["wind_speed"] >= wind_threshold
        self.gdf["is_flood"] = self.gdf["rain_mm"] >= rain_threshold
        self.gdf["risk_level"] = "normal"

        self.gdf.loc[self.gdf["is_flood"], "risk_level"] = "flood"
        self.gdf.loc[self.gdf["is_storm"], "risk_level"] = "storm"
        self.gdf.loc[self.gdf["is_storm"] & self.gdf["is_flood"], "risk_level"] = "severe"

        print(f"[INFO] Classified risk levels for {len(self.gdf)} points.")

    def export_processed_data(self):
        """Sauvegarde les données nettoyées dans un nouveau fichier"""
        print(f"[INFO] Saving processed weather data to {self.output_path}")
        self.gdf.to_file(self.output_path, driver="GeoJSON")
        print("[INFO] Export complete.")

    def get_risk_penalties(self):
        """
        Retourne un dictionnaire de pénalités par géopoint (hashé) selon le risque météo
        Utilisable dans `graph_weighing.py`
        """
        print("[INFO] Generating weather penalties...")

        penalties = {}
        for _, row in self.gdf.iterrows():
            location_id = hash(row["geometry"].wkt)
            level = row["risk_level"]
            if level == "normal":
                penalty = 1.0
            elif level == "flood":
                penalty = 2.5
            elif level == "storm":
                penalty = 3.0
            elif level == "severe":
                penalty = float("inf")  # zone à éviter
            else:
                penalty = 1.0
            penalties[location_id] = penalty
        return penalties

    def as_json(self):
        """Retourne les données météo pour affichage sur la carte du dashboard"""
        return json.loads(self.gdf.to_json())

# Exemple d'utilisation
if __name__ == "__main__":
    processor = WeatherProcessor(
        input_path="data/weather_raw.geojson",
        output_path="data/weather_processed.geojson"
    )
    processor.load_data()
    processor.preprocess_data()
    processor.classify_risk()
    processor.export_processed_data()
