import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import json

class HazardProcessor:
    def __init__(self, input_path="data/hazards_raw.geojson", output_path="data/hazards_processed.geojson"):
        self.input_path = input_path
        self.output_path = output_path
        self.gdf = None

    def load_data(self):
        """ Charge les données de danger en format GeoJSON """
        print(f"[INFO] Loading hazard data from {self.input_path}")
        self.gdf = gpd.read_file(self.input_path)
        print(f"[INFO] Loaded {len(self.gdf)} hazard records.")

    def preprocess_data(self):
        """ Nettoie et normalise les données de danger """
        if self.gdf is None:
            raise ValueError("Data not loaded.")

        print("[INFO] Preprocessing hazard data...")

        # Exemple : garder seulement les colonnes utiles
        self.gdf = self.gdf[["geometry", "hazard_type", "severity", "timestamp"]]

        # Convertir les timestamps
        self.gdf["timestamp"] = pd.to_datetime(self.gdf["timestamp"])

        # Remplir les valeurs manquantes
        self.gdf["severity"] = self.gdf["severity"].fillna("unknown")

        # Filtrer les enregistrements invalides
        self.gdf = self.gdf[self.gdf.geometry.notnull()]
        print(f"[INFO] Preprocessed {len(self.gdf)} valid records.")

    def identify_danger_zones(self, severity_threshold="medium"):
        """
        Filtrer les zones à risque selon un seuil de gravité.
        Par exemple : ['low', 'medium', 'high']
        """
        print(f"[INFO] Filtering hazards with severity >= {severity_threshold}")
        severity_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}

        def is_severe(sev):
            return severity_rank.get(sev, 0) >= severity_rank.get(severity_threshold, 2)

        self.gdf = self.gdf[self.gdf["severity"].apply(is_severe)]
        print(f"[INFO] Retained {len(self.gdf)} hazardous zones.")

    def export_processed_data(self):
        """ Sauvegarde les données traitées pour d'autres modules """
        print(f"[INFO] Saving processed hazard data to {self.output_path}")
        self.gdf.to_file(self.output_path, driver="GeoJSON")
        print("[INFO] Export complete.")

    def as_json(self):
        """ Exporte les données comme objet JSON (utile pour dashboard/API) """
        return json.loads(self.gdf.to_json())

# Exemple d'utilisation
if __name__ == "__main__":
    processor = HazardProcessor(
        input_path="data/hazards_raw.geojson",
        output_path="data/hazards_processed.geojson"
    )
    processor.load_data()
    processor.preprocess_data()
    processor.identify_danger_zones(severity_threshold="medium")
    processor.export_processed_data()
