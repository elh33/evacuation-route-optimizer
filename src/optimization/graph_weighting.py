import networkx as nx
from typing import Dict, Any

class GraphWeighing:
    """Class to dynamically update and calculate weights for graph edges based on various factors."""
    
    def __init__(self, graph: nx.Graph, risk_factor: float = 0.7, time_factor: float = 0.3):
        """
        Initialize the graph weighing with factors for risk and time.
        
        Args:
            graph: Road network graph (nodes and edges with attributes like length and risk)
            risk_factor: Weight for risk in edge cost calculation (0 to 1)
            time_factor: Weight for time in edge cost calculation (0 to 1)
        """
        self.graph = graph
        self.risk_factor = risk_factor
        self.time_factor = time_factor

        # Normalize the weights to make sure they sum to 1
        total = risk_factor + time_factor
        self.risk_factor /= total
        self.time_factor /= total
    
    def calculate_edge_cost(self, u: int, v: int, edge_data: Dict[str, Any]) -> float:
        """
        Calculate the combined cost of an edge based on risk and time factors.
        
        Args:
            u: Source node ID
            v: Target node ID
            edge_data: Dictionary with edge attributes (e.g., 'length', 'risk')
            
        Returns:
            float: Combined edge cost
        """
        # Default edge length (meters)
        length = edge_data.get('length', 100)
        
        # Default time calculation (assuming 30 km/h ~ 8.33 m/s as average speed)
        travel_time = length / 8.33  # Time in seconds
        travel_time_hours = travel_time / 3600  # Convert to hours
        
        # Default risk value (if not provided)
        risk = edge_data.get('risk', 0.5)
        
        # Calculate weighted edge cost based on risk and time
        return self.risk_factor * risk + self.time_factor * travel_time_hours
    
    def update_edge_weights(self, u: int, v: int, edge_data: Dict[str, Any]) -> None:
        """
        Update the weights of the edges based on new conditions like risk or traffic changes.
        
        Args:
            u: Source node ID
            v: Target node ID
            edge_data: Dictionary with new edge attributes (e.g., new risk or traffic data)
        """
        # Update edge attributes (length, risk, traffic, etc.)
        if 'length' in edge_data:
            self.graph[u][v]['length'] = edge_data['length']
        
        if 'risk' in edge_data:
            self.graph[u][v]['risk'] = edge_data['risk']
        
        # Recalculate the cost for the edge with new attributes
        self.graph[u][v]['cost'] = self.calculate_edge_cost(u, v, self.graph[u][v])
        
    def refresh_all_edge_weights(self) -> None:
        """Recalculate and update all edges in the graph to reflect new weights."""
        for u, v, data in self.graph.edges(data=True):
            data['cost'] = self.calculate_edge_cost(u, v, data)
    
    def apply_traffic_updates(self, traffic_data: Dict[Tuple[int, int], float]) -> None:
        """
        Apply real-time traffic updates to adjust edge weights dynamically.
        
        Args:
            traffic_data: Dictionary where keys are edge tuples (u, v), and values are updated traffic times
        """
        for (u, v), traffic_time in traffic_data.items():
            # Adjust the travel time on the edge based on traffic updates
            if (u, v) in self.graph.edges:
                # Adjust the length based on traffic time (traffic is proportional to time)
                length = self.graph[u][v]['length']
                updated_time = traffic_time
                self.graph[u][v]['length'] = updated_time * 8.33  # Estimate new length from traffic time
                self.update_edge_weights(u, v, self.graph[u][v])
    
    def apply_risk_updates(self, risk_data: Dict[Tuple[int, int], float]) -> None:
        """
        Apply risk level updates to adjust edge weights dynamically.
        
        Args:
            risk_data: Dictionary where keys are edge tuples (u, v), and values are updated risk levels.
        """
        for (u, v), risk_level in risk_data.items():
            # Adjust the risk value on the edge based on risk updates
            if (u, v) in self.graph.edges:
                self.graph[u][v]['risk'] = risk_level
                self.update_edge_weights(u, v, self.graph[u][v])

# Example usage:
if __name__ == "__main__":
    # Create a sample road network graph with nodes and edges
    G = nx.Graph()
    G.add_nodes_from([
        (0, {'x': 0, 'y': 0}),
        (1, {'x': 1, 'y': 2}),
        (2, {'x': 3, 'y': 3}),
        (3, {'x': 5, 'y': 5}),
    ])
    G.add_edges_from([
        (0, 1, {'length': 100, 'risk': 0.5}),
        (1, 2, {'length': 150, 'risk': 0.6}),
        (2, 3, {'length': 200, 'risk': 0.7}),
    ])
    
    # Initialize GraphWeighing class
    graph_weigher = GraphWeighing(G)

    # Refresh the weights of all edges based on the initial attributes
    graph_weigher.refresh_all_edge_weights()

    # Apply traffic update (e.g., new traffic delays)
    traffic_data = {
        (1, 2): 200,  # Increase travel time due to traffic (e.g., 200 seconds)
        (2, 3): 250,  # Increase travel time due to traffic
    }
    graph_weigher.apply_traffic_updates(traffic_data)
    
    # Apply risk updates (e.g., a road hazard increases risk)
    risk_data = {
        (0, 1): 0.8,  # Increase risk on the road due to hazard
    }
    graph_weigher.apply_risk_updates(risk_data)

    # Print updated edge weights (costs)
    for u, v, data in G.edges(data=True):
        print(f"Edge ({u}, {v}): Cost = {data['cost']:.2f}")
