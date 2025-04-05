import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt

class GraphBuilder:
    def __init__(self, location, network_type="drive"):
        """
        Initializes the GraphBuilder.

        :param location: The location name (e.g., city or region) to retrieve OSM data.
        :param network_type: The type of road network ('drive', 'walk', 'bike').
        """
        self.location = location
        self.network_type = network_type
        self.graph = None

    def build_graph(self):
        """
        Builds a graph from OpenStreetMap data for the specified location.
        The graph will include road segments as edges and intersections as nodes.
        """
        print(f"Building graph for {self.location} using {self.network_type} network.")
        
        # Get the graph from OSM using osmnx
        self.graph = ox.graph_from_place(self.location, network_type=self.network_type)
        
        # Simplify the graph to remove parallel edges
        self.graph = ox.utils_graph.get_digraph(self.graph)
        print(f"Graph built successfully with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges.")
        
        # Add additional attributes like road length and speed limit (optional)
        self.add_edge_attributes()

    def add_edge_attributes(self):
        """
        Add attributes like road length and speed limit to each edge in the graph.
        """
        # Add the length of each road segment (in meters)
        for u, v, data in self.graph.edges(data=True):
            data['length'] = ox.distance.great_circle_vec(self.graph.nodes[u]['y'], self.graph.nodes[u]['x'],
                                                         self.graph.nodes[v]['y'], self.graph.nodes[v]['x'])
            data['speed_limit'] = data.get('maxspeed', 50)  # Default speed limit is 50 km/h if not specified

    def save_graph(self, filename="evacuation_graph.gml"):
        """
        Saves the constructed graph to a file (GML format).
        
        :param filename: The name of the file to save the graph.
        """
        print(f"Saving graph to {filename}.")
        nx.write_gml(self.graph, filename)
        print("Graph saved successfully.")

    def load_graph(self, filename="evacuation_graph.gml"):
        """
        Loads a previously saved graph from a file.
        
        :param filename: The file to load the graph from.
        """
        print(f"Loading graph from {filename}.")
        self.graph = nx.read_gml(filename)
        print(f"Graph loaded with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges.")
        
    def visualize_graph(self):
        """
        Visualizes the graph using Matplotlib.
        """
        print("Visualizing graph.")
        fig, ax = plt.subplots(figsize=(12, 12))
        pos = {node: (data['x'], data['y']) for node, data in self.graph.nodes(data=True)}
        nx.draw(self.graph, pos, with_labels=False, node_size=10, node_color="blue", edge_color="gray", width=0.5, ax=ax)
        plt.title(f"{self.location} Evacuation Network")
        plt.show()

# Example usage
if __name__ == "__main__":
    location = "Los Angeles, California"  # Replace with your desired location
    graph_builder = GraphBuilder(location, network_type="drive")

    # Build and visualize the graph
    graph_builder.build_graph()
    graph_builder.visualize_graph()

    # Save the graph to a file
    graph_builder.save_graph("la_evacuation_graph.gml")

    # Load and visualize a previously saved graph
    graph_builder.load_graph("la_evacuation_graph.gml")
    graph_builder.visualize_graph()
