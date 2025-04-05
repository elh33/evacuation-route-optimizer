import requests
import json
import networkx as nx

class TrafficCollector:
    def __init__(self, graph, traffic_api_key, traffic_api_url="https://maps.googleapis.com/maps/api/traffic"):
        """
        Initializes the TrafficCollector.
        
        :param graph: The evacuation network graph (usually from OSM data).
        :param traffic_api_key: The API key to access traffic data.
        :param traffic_api_url: The URL for the traffic data API (default is for Google Maps API).
        """
        self.graph = graph
        self.traffic_api_key = traffic_api_key
        self.traffic_api_url = traffic_api_url

    def get_traffic_data(self, origin, destination):
        """
        Fetches traffic data between the origin and destination using the traffic API.
        
        :param origin: The starting point (lat, lon).
        :param destination: The endpoint (lat, lon).
        :return: A dictionary with traffic information like travel time, congestion, etc.
        """
        # Construct the traffic API request URL
        url = f"{self.traffic_api_url}/directions/json"
        params = {
            "origin": f"{origin[0]},{origin[1]}",
            "destination": f"{destination[0]},{destination[1]}",
            "key": self.traffic_api_key,
            "departure_time": "now"
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            traffic_data = response.json()
            if traffic_data['status'] == 'OK':
                return traffic_data['routes'][0]['legs'][0]
            else:
                raise Exception(f"Error fetching traffic data: {traffic_data['status']}")
        else:
            raise Exception(f"Failed to retrieve traffic data: {response.status_code}")

    def update_graph_with_traffic(self):
        """
        Updates the evacuation graph with traffic data by adding congestion information.
        Each edge is updated with a 'traffic_congestion' attribute, which could affect evacuation planning.
        """
        for u, v, data in self.graph.edges(data=True):
            # Get lat, lon for both nodes (u and v) from graph data
            lat_u, lon_u = self.graph.nodes[u]['pos']
            lat_v, lon_v = self.graph.nodes[v]['pos']
            
            try:
                # Fetch traffic data for the edge (u, v)
                traffic_info = self.get_traffic_data((lat_u, lon_u), (lat_v, lon_v))
                
                # Extract relevant traffic information (e.g., duration, congestion)
                duration = traffic_info['duration']['value']  # in seconds
                congestion = traffic_info['duration_in_traffic']['value']  # in seconds

                # Update the edge with traffic congestion info
                self.graph[u][v]['traffic_congestion'] = congestion
                self.graph[u][v]['duration'] = duration
                self.graph[u][v]['congestion_ratio'] = congestion / duration  # ratio of congestion to normal duration

            except Exception as e:
                print(f"Error updating edge ({u}, {v}): {e}")

    def save_traffic_data(self, filename='traffic_data.json'):
        """
        Saves the traffic data to a file.
        
        :param filename: The file where the traffic data will be saved.
        """
        traffic_data = {
            'nodes': list(self.graph.nodes(data=True)),
            'edges': [(u, v, data) for u, v, data in self.graph.edges(data=True)]
        }
        with open(filename, 'w') as file:
            json.dump(traffic_data, file)

    def load_traffic_data(self, filename='traffic_data.json'):
        """
        Loads traffic data from a saved file.
        
        :param filename: The file from which to load the traffic data.
        """
        with open(filename, 'r') as file:
            traffic_data = json.load(file)
        
        for node, data in traffic_data['nodes']:
            self.graph.add_node(node, **data)
        
        for u, v, data in traffic_data['edges']:
            self.graph.add_edge(u, v, **data)

    def visualize_traffic_graph(self):
        """
        Visualizes the evacuation graph with traffic congestion information.
        Uses different edge colors based on the traffic congestion ratio.
        """
        import matplotlib.pyplot as plt
        import networkx as nx

        edge_colors = []
        for u, v, data in self.graph.edges(data=True):
            congestion_ratio = data.get('congestion_ratio', 0)
            if congestion_ratio > 0.5:
                edge_colors.append('red')
            elif congestion_ratio > 0.2:
                edge_colors.append('yellow')
            else:
                edge_colors.append('green')

        pos = {node: (data['pos'][0], data['pos'][1]) for node, data in self.graph.nodes(data=True)}
        nx.draw(self.graph, pos, with_labels=True, node_size=50, font_size=8, edge_color=edge_colors, width=2)
        plt.title("Evacuation Network with Traffic Conditions")
        plt.show()

# Example usage
if __name__ == "__main__":
    # Example graph with sample nodes and edges
    G = nx.Graph()

    # Adding nodes with positions (latitude, longitude)
    G.add_node(1, pos=(51.5074, -0.1278))  # London
    G.add_node(2, pos=(51.5154, -0.1419))  # King's Cross
    G.add_node(3, pos=(51.5034, -0.1198))  # Tower Bridge

    # Adding edges between nodes (with initial weights)
    G.add_edge(1, 2, weight=2.0)
    G.add_edge(2, 3, weight=3.0)

    # Traffic Collector instance
    traffic_api_key = "YOUR_GOOGLE_MAPS_API_KEY"
    traffic_collector = TrafficCollector(G, traffic_api_key)

    # Update the graph with real-time traffic data
    traffic_collector.update_graph_with_traffic()

    # Save the traffic data to a file
    traffic_collector.save_traffic_data()

    # Load traffic data from the file
    traffic_collector.load_traffic_data()

    # Visualize the traffic-affected evacuation network
    traffic_collector.visualize_traffic_graph()
