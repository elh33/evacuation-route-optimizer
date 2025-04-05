import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import json
import datetime

class TrafficProcessor:
    def __init__(self, input_path="data/traffic_raw.geojson", output_path="data/traffic_processed.geojson"):
        self.input_path = input_path
        self.output_path = output_path
        self.gdf = None

    def load_data(self):
        """Charge les données de trafic à partir d’un fichier GeoJSON."""
        print(f"[INFO] Loading traffic data from {self.input_path}")
        self.gdf = gpd.read_file(self.input_path)
        print(f"[INFO] Loaded {len(self.gdf)} traffic segments.")

    def preprocess_data(self):
        """Nettoie et standardise les données de trafic."""
        if self.gdf is None:
            raise ValueError("Data not loaded.")

        print("[INFO] Preprocessing traffic data...")

        # Garder les colonnes essentielles
        columns_needed = ["geometry", "status", "congestion_level", "timestamp"]
        self.gdf = self.gdf[[col for col in columns_needed if col in self.gdf.columns]]

        # Convertir la date
        self.gdf["timestamp"] = pd.to_datetime(self.gdf["timestamp"], errors='coerce')

        # Normaliser les champs
        self.gdf["congestion_level"] = self.gdf["congestion_level"].fillna("unknown").str.lower()
        self.gdf["status"] = self.gdf["status"].fillna("open").str.lower()

        # Supprimer les entrées sans géométrie
        self.gdf = self.gdf[self.gdf.geometry.notnull()]
        print(f"[INFO] Preprocessed {len(self.gdf)} valid traffic segments.")

    def identify_traffic_issues(self):
        """Filtre les routes avec congestion ou fermetures."""
        print("[INFO] Identifying problematic traffic segments...")

        self.gdf["is_blocked"] = self.gdf["status"].isin(["closed", "blocked"])
        self.gdf["is_congested"] = self.gdf["congestion_level"].isin(["high", "severe"])

        issues = self.gdf[self.gdf["is_blocked"] | self.gdf["is_congested"]]
        print(f"[INFO] Found {len(issues)} critical traffic issues.")
        return issues

    def export_processed_data(self):
        """Sauvegarde les données filtrées dans un nouveau fichier GeoJSON."""
        print(f"[INFO] Saving processed traffic data to {self.output_path}")
        self.gdf.to_file(self.output_path, driver="GeoJSON")
        print("[INFO] Export complete.")

    def get_segment_penalties(self):
        """
        Génère un dictionnaire pour pondérer les routes selon leur statut
        Utilisable par graph_weighing.py
        """
        print("[INFO] Generating penalties for traffic segments...")

        penalties = {}
        for _, row in self.gdf.iterrows():
            segment_id = hash(row["geometry"].wkt)
            if row["is_blocked"]:
                penalty = float("inf")
            elif row["is_congested"]:
                penalty = 3.0  # facteur multiplicatif sur la durée
            else:
                penalty = 1.0
            penalties[segment_id] = penalty
        return penalties

    def as_json(self):
        """Retourne les données prêtes pour affichage ou API."""
        return json.loads(self.gdf.to_json())

# Exemple d'utilisation
if __name__ == "__main__":
    processor = TrafficProcessor(
        input_path="data/traffic_raw.geojson",
        output_path="data/traffic_processed.geojson"
    )
    processor.load_data()
    processor.preprocess_data()
    processor.identify_traffic_issues()
    processor.export_processed_data()
