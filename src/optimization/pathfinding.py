import networkx as nx
import numpy as np
from typing import List, Tuple, Dict, Optional, Any

class AStarPathfinder:
    """A* algorithm implementation for finding optimal evacuation routes.
    
    This implementation considers both risk levels and travel time to optimize routes.
    """
    
    def __init__(self, risk_weight: float = 0.7, time_weight: float = 0.3):
        """Initialize the A* pathfinder with weights for risk and time.
        
        Args:
            risk_weight: Weight for risk factor (0 to 1)
            time_weight: Weight for time factor (0 to 1)
        """
        # Ensure weights sum to 1
        total = risk_weight + time_weight
        self.risk_weight = risk_weight / total
        self.time_weight = time_weight / total
    
    def calc_edge_cost(self, u: int, v: int, data: Dict[str, Any]) -> float:
        """Calculate the cost of traversing an edge.
        
        Args:
            u: Source node
            v: Target node
            data: Edge data dictionary
            
        Returns:
            float: Combined cost considering risk and travel time
        """
        # Extract or calculate metrics
        # Default length (in meters) if not available
        length = data.get('length', 100)
        
        # Default travel time based on length (assume 30 km/h ~ 8.33 m/s on average)
        time_cost = length / 8.33
        
        # Default risk if not available
        risk = data.get('risk', 0.5)
        
        # Combine metrics with weights
        return self.risk_weight * risk + self.time_weight * (time_cost / 3600)  # Normalize time to [0,1]
        
    def heuristic(self, u: int, v: int, graph: nx.Graph) -> float:
        """Calculate heuristic (straight-line distance).
        
        Args:
            u: Current node
            v: Target node
            graph: Road network graph
            
        Returns:
            float: Estimated cost to reach the target
        """
        # Extract coordinates
        u_x, u_y = graph.nodes[u]['x'], graph.nodes[u]['y']
        v_x, v_y = graph.nodes[v]['x'], graph.nodes[v]['y']
        
        # Calculate Euclidean distance
        dist = ((u_x - v_x) ** 2 + (u_y - v_y) ** 2) ** 0.5
        
        # Return normalized distance 
        # Assuming average speed of 30 km/h and coordinates in degrees (approx 111km per degree)
        return dist * 111000 / 30000  # Convert to hours
    
    def find_path(self, graph: nx.Graph, start: int, end: int) -> Tuple[List[int], float]:
        """Find the optimal path using A* algorithm.
        
        Args:
            graph: Road network graph
            start: Starting node
            end: Destination node
            
        Returns:
            Tuple containing:
                - List of node IDs forming the path
                - Total cost of the path
        """
        # Check if nodes exist in the graph
        if start not in graph.nodes or end not in graph.nodes:
            return [], float('inf')
        
        # Use NetworkX's A* implementation
        try:
            path = nx.astar_path(
                graph, 
                start, 
                end, 
                heuristic=lambda u, v: self.heuristic(u, v, graph),
                weight=lambda u, v, data: self.calc_edge_cost(u, v, data)
            )
            
            # Calculate the total cost of the path
            cost = 0
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                # Handle multigraphs
                if isinstance(graph, nx.MultiGraph) or isinstance(graph, nx.MultiDiGraph):
                    edge_data = graph[u][v][0]  # Get first edge between nodes
                else:
                    edge_data = graph[u][v]
                cost += self.calc_edge_cost(u, v, edge_data)
                     
            return path, cost
            
        except nx.NetworkXNoPath:
            return [], float('inf')
    
    def find_multiple_paths(self, graph: nx.Graph, start: int, end: int, 
                          num_paths: int = 3, diversity_factor: float = 0.3) -> List[Tuple[List[int], float]]:
        """Find multiple diverse evacuation routes.
        
        Args:
            graph: Road network graph
            start: Starting node
            end: Destination node
            num_paths: Number of paths to find
            diversity_factor: Factor to control how different paths should be
            
        Returns:
            List of tuples, each containing:
                - List of node IDs forming the path
                - Total cost of the path
        """
        paths = []
        
        # Find the first optimal path
        first_path, first_cost = self.find_path(graph, start, end)
        
        if not first_path:
            return paths
            
        paths.append((first_path, first_cost))
        
        # Make a copy of the graph to modify edge weights
        modified_graph = graph.copy()
        
        # Find additional diverse paths
        for i in range(1, num_paths):
            # Penalize edges in the previous paths
            for path, _ in paths:
                for j in range(len(path) - 1):
                    u, v = path[j], path[j + 1]
                    
                    # Skip if edge no longer exists
                    if not modified_graph.has_edge(u, v):
                        continue
                    
                    # Add penalty to edges in previous paths
                    # Handle multigraphs
                    if isinstance(modified_graph, nx.MultiGraph) or isinstance(modified_graph, nx.MultiDiGraph):
                        for k in modified_graph[u][v]:
                            # Increase risk to discourage reuse
                            if 'risk' in modified_graph[u][v][k]:
                                modified_graph[u][v][k]['risk'] = min(
                                    1.0, 
                                    modified_graph[u][v][k]['risk'] + diversity_factor
                                )
                            else:
                                modified_graph[u][v][k]['risk'] = diversity_factor
                    else:
                        # For simple graphs
                        if 'risk' in modified_graph[u][v]:
                            modified_graph[u][v]['risk'] = min(
                                1.0,
                                modified_graph[u][v]['risk'] + diversity_factor
                            )
                        else:
                            modified_graph[u][v]['risk'] = diversity_factor
            
            # Find another path with the modified graph
            next_path, next_cost = self.find_path(modified_graph, start, end)
            
            if next_path:
                paths.append((next_path, next_cost))
            else:
                break
                
        return paths