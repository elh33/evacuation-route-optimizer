import networkx as nx
from typing import List, Tuple, Dict, Any
from collections import deque

class EvacuationPlanner:
    """Class to handle evacuation planning with A* pathfinding and resource management."""
    
    def __init__(self, graph: nx.Graph, risk_weight: float = 0.7, time_weight: float = 0.3):
        """
        Initialize the EvacuationPlanner with graph and weights for risk and time.

        Args:
            graph: Road network graph (nodes with coordinates, edges with length and risk)
            risk_weight: Weight for risk factor (0 to 1)
            time_weight: Weight for time factor (0 to 1)
        """
        self.graph = graph
        self.pathfinder = AStarPathfinder(risk_weight, time_weight)
    
    def get_safe_zones(self) -> List[int]:
        """Return a list of safe zones (nodes that represent evacuation points)."""
        return [node for node, data in self.graph.nodes(data=True) if data.get('safe_zone', False)]

    def get_critical_zones(self) -> List[int]:
        """Return a list of critical zones (nodes that represent high-risk areas)."""
        return [node for node, data in self.graph.nodes(data=True) if data.get('risk', 1.0) > 0.7]

    def plan_evacuations(self, start: int, end: int, num_paths: int = 3) -> List[Dict[str, Any]]:
        """
        Plan the evacuation by finding multiple evacuation paths.

        Args:
            start: The starting node (e.g., current location of people or a building).
            end: The end node (e.g., a safe zone).
            num_paths: Number of diverse paths to find.
            
        Returns:
            List of dictionaries with details about each path, including route and cost.
        """
        evacuation_routes = []
        paths = self.pathfinder.find_multiple_paths(self.graph, start, end, num_paths)
        
        for path, cost in paths:
            evacuation_routes.append({
                "path": path,
                "cost": cost,
                "path_length": len(path),
                "critical_zones_crossed": [node for node in path if node in self.get_critical_zones()],
                "safe_zones_reached": [node for node in path if node in self.get_safe_zones()]
            })
        
        return evacuation_routes

    def alert_residents(self, evacuation_routes: List[Dict[str, Any]]) -> None:
        """
        Send alerts to residents or staff with evacuation instructions.

        Args:
            evacuation_routes: The evacuation routes to be communicated.
        """
        for route in evacuation_routes:
            # Simulate sending alerts (e.g., by email, SMS, or push notifications)
            print(f"Evacuation Alert: Follow the path {route['path']} to safety.")
            print(f"Critical zones crossed: {route['critical_zones_crossed']}")
            print(f"Safe zones reached: {route['safe_zones_reached']}")
            print(f"Total cost: {route['cost']:.2f}\n")

    def manage_resources(self) -> None:
        """Manage resources like medical kits, food, etc., during the evacuation."""
        # Simulate resource management (e.g., ensuring safe zones are equipped)
        safe_zones = self.get_safe_zones()
        for zone in safe_zones:
            print(f"Resource check at Safe Zone {zone}: Ensure medical kits, food, and water are available.")
    
    def simulate_evacuations(self, start: int, num_paths: int = 3) -> List[Dict[str, Any]]:
        """Simulate evacuation from a given starting point."""
        evacuation_routes = self.plan_evacuations(start, self.get_safe_zones()[0], num_paths)
        self.alert_residents(evacuation_routes)
        self.manage_resources()
        return evacuation_routes

    def visualize_routes(self, evacuation_routes: List[Dict[str, Any]]) -> None:
        """Visualize the evacuation routes on a map (using NetworkX)."""
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 8))
        pos = {node: (data['x'], data['y']) for node, data in self.graph.nodes(data=True)}
        nx.draw(self.graph, pos, with_labels=True, node_size=500, node_color='lightblue', font_size=12)
        
        for route in evacuation_routes:
            path = route["path"]
            edges = list(zip(path[:-1], path[1:]))
            nx.draw_networkx_edges(self.graph, pos, edgelist=edges, edge_color='red', width=2)
        
        plt.title("Evacuation Routes")
        plt.show()

# Example usage:
if __name__ == "__main__":
    # Example road network graph with coordinates
    G = nx.Graph()
    G.add_nodes_from([
        (0, {'x': 0, 'y': 0, 'safe_zone': True}),
        (1, {'x': 1, 'y': 2, 'risk': 0.5}),
        (2, {'x': 3, 'y': 3, 'risk': 0.8}),
        (3, {'x': 5, 'y': 5, 'safe_zone': True}),
        (4, {'x': 6, 'y': 7, 'risk': 0.9}),
    ])
    G.add_edges_from([
        (0, 1, {'length': 100, 'risk': 0.5}),
        (1, 2, {'length': 150, 'risk': 0.7}),
        (2, 3, {'length': 200, 'risk': 0.6}),
        (3, 4, {'length': 250, 'risk': 0.9}),
    ])

    planner = EvacuationPlanner(G)
    routes = planner.simulate_evacuations(start=1, num_paths=3)
    planner.visualize_routes(routes)
