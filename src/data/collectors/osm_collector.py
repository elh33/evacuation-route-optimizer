"""Module for collecting OpenStreetMap data."""

import osmnx as ox
import networkx as nx
import geopandas as gpd
import pandas as pd
import numpy as np
import os
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

class OSMCollector:
    """Class to collect and process OpenStreetMap data."""
    
    def __init__(self, data_dir: Path):
        """Initialize the OSM collector.
        
        Args:
            data_dir: Directory where the OSM data will be stored
        """
        self.data_dir = data_dir
        self.osm_dir = data_dir / "raw" / "osm"
        self.osm_dir.mkdir(exist_ok=True, parents=True)
        
        # Configure OSMnx
        ox.config(use_cache=True, log_console=True)
        
    def download_city_network(self, city_name: str, network_type: str = 'drive') -> nx.MultiDiGraph:
        """Download the road network for a city.
        
        Args:
            city_name: Name of the city (e.g., "Paris, France")
            network_type: Type of network ('drive', 'walk', 'bike', 'all')
            
        Returns:
            NetworkX graph of the road network
        """
        logging.info(f"Downloading {network_type} network for {city_name}")
        
        try:
            # Download the network
            G = ox.graph_from_place(city_name, network_type=network_type)
            
            # Save to file
            self._save_network(G, city_name, network_type)
            
            return G
            
        except Exception as e:
            logging.error(f"Error downloading network for {city_name}: {str(e)}")
            raise
    
    def load_city_network(self, city_name: str, network_type: str = 'drive') -> Optional[nx.MultiDiGraph]:
        """Load a previously downloaded road network.
        
        Args:
            city_name: Name of the city
            network_type: Type of network
            
        Returns:
            NetworkX graph of the road network, or None if not found
        """
        file_path = self._get_network_path(city_name, network_type)
        
        if file_path.exists():
            try:
                logging.info(f"Loading network for {city_name} from {file_path}")
                return nx.read_gpickle(file_path)
            except Exception as e:
                logging.error(f"Error loading network for {city_name}: {str(e)}")
                return None
        else:
            logging.warning(f"No saved network found for {city_name}")
            return None
    
    def get_city_network(self, city_name: str, network_type: str = 'drive', force_download: bool = False) -> nx.MultiDiGraph:
        """Get the road network for a city, downloading it if necessary.
        
        Args:
            city_name: Name of the city
            network_type: Type of network
            force_download: Whether to force a fresh download
            
        Returns:
            NetworkX graph of the road network
        """
        if not force_download:
            # Try to load from file first
            G = self.load_city_network(city_name, network_type)
            if G is not None:
                return G
        
        # Download if not found or force_download is True
        return self.download_city_network(city_name, network_type)
    
    def get_network_stats(self, G: nx.MultiDiGraph) -> Dict[str, Any]:
        """Get basic statistics about the network.
        
        Args:
            G: NetworkX graph
            
        Returns:
            Dictionary of network statistics
        """
        return {
            'num_nodes': len(G.nodes),
            'num_edges': len(G.edges),
            'avg_node_degree': np.mean([d for n, d in G.degree()]),
            'network_type': G.graph.get('network_type', 'unknown')
        }
    
    def _save_network(self, G: nx.MultiDiGraph, city_name: str, network_type: str) -> None:
        """Save a network graph to disk.
        
        Args:
            G: NetworkX graph
            city_name: Name of the city
            network_type: Type of network
        """
        file_path = self._get_network_path(city_name, network_type)
        
        try:
            # Save the graph
            nx.write_gpickle(G, file_path)
            logging.info(f"Saved network for {city_name} to {file_path}")
            
            # Also save a GeoJSON for visualization
            nodes, edges = ox.graph_to_gdfs(G)
            edges.to_file(file_path.with_suffix('.geojson'), driver='GeoJSON')
            
        except Exception as e:
            logging.error(f"Error saving network for {city_name}: {str(e)}")
    
    def _get_network_path(self, city_name: str, network_type: str) -> Path:
        """Get the file path for a network.
        
        Args:
            city_name: Name of the city
            network_type: Type of network
            
        Returns:
            Path to the network file
        """
        # Sanitize city name for file path
        city_file_name = city_name.replace(',', '').replace(' ', '_').lower()
        
        return self.osm_dir / f"{city_file_name}_{network_type}.gpickle"