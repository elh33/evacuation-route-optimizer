import geopandas as gpd
from shapely.geometry import Point
import os

class DataSynchronizer:
    def __init__(
        self,
        hazard_path="data/hazards_processed.geojson",
        weather_path="data/weather_processed.geojson",
        traffic_path="data/traffic_processed.geojson",
        osm_path="data/osm_processed.geojson",
        output_path="data/synchronized_data.geojson"
    ):
        self.paths = {
            "hazard": hazard_path,
            "weather": weather_path,
            "traffic": traffic_path,
            "osm": osm_path
        }
        self.output_path = output_path
        self.dataframes = {}
        self.synchronized_gdf = None

    def load_data(self):
        """Charge toutes les couches GeoJSON disponibles"""
        print("[INFO] Loading data layers...")
        for key, path in self.paths.items():
            if os.path.exists(path):
                self.dataframes[key] = gpd.read_file(path)
                print(f"  ✔ Loaded {key} with {len(self.dataframes[key])} features.")
            else:
                print(f"  ⚠ {key} file not found at {path}.")

    def merge_all_layers(self):
        """Fusionne les layers autour des coordonnées GPS, avec une tolérance spatiale"""
        print("[INFO] Merging all layers...")

        base = self.dataframes.get("osm", gpd.GeoDataFrame(geometry=[]))  # base = routes OSM
        base = base.set_geometry("geometry")

        for key in ["hazard", "weather", "traffic"]:
            df = self.dataframes.get(key)
            if df is not None:
                print(f"  ⤷ Merging {key}...")
                df = df.set_geometry("geometry")
                base = gpd.sjoin_nearest(base, df, how="left", distance_col=f"{key}_distance", max_distance=50)
                # max_distance = 50m tolérance spatiale

        self.synchronized_gdf = base
        print(f"[INFO] Total synchronized points: {len(self.synchronized_gdf)}")

    def export(self):
        """Sauvegarde la couche fusionnée"""
        print(f"[INFO] Exporting to {self.output_path}")
        self.synchronized_gdf.to_file(self.output_path, driver="GeoJSON")
        print("[INFO] Synchronization complete.")

    def get_unified_features(self):
        """Retourne les données synchronisées sous forme dict pour usage programmatique (ex: dashboard)"""
        return self.synchronized_gdf.to_dict("records")

# Exemple d’utilisation
if __name__ == "__main__":
    sync = DataSynchronizer()
    sync.load_data()
    sync.merge_all_layers()
    sync.export()
