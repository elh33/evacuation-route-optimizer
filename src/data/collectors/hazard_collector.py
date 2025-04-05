import random
import time
import json
import pandas as pd
import networkx as nx

class HazardCollector:
    def __init__(self, graph: nx.Graph):
        self.graph = graph  # The evacuation network graph
        self.hazards = []  # List to store hazard data

    def collect_hazard_data(self):
        """
        Simulates the collection of hazard data. In a real-world scenario,
        this would gather data from sensors, APIs, or user input.
        """
        hazard_types = ['Fire', 'Flood', 'Earthquake', 'Traffic Accident']
        hazard_severity = ['Low', 'Medium', 'High']
        
        # Simulating hazard data collection at random nodes and edges
        for node in self.graph.nodes:
            hazard_type = random.choice(hazard_types)
            severity = random.choice(hazard_severity)
            risk_level = self.calculate_risk_level(hazard_type, severity)

            hazard_data = {
                'node': node,
                'type': hazard_type,
                'severity': severity,
                'risk_level': risk_level,
                'timestamp': time.time()  # Current timestamp for when hazard is recorded
            }
            self.hazards.append(hazard_data)

            # Optionally, attach this hazard data to the node in the graph
            self.graph.nodes[node]['hazard'] = hazard_data

    def calculate_risk_level(self, hazard_type: str, severity: str) -> float:
        """
        Calculate a risk level based on the hazard type and severity.
        Risk levels are between 0 (no risk) and 1 (maximum risk).
        """
        # Define risk multipliers for each hazard type and severity level
        risk_factors = {
            'Fire': {'Low': 0.3, 'Medium': 0.6, 'High': 1.0},
            'Flood': {'Low': 0.4, 'Medium': 0.7, 'High': 1.0},
            'Earthquake': {'Low': 0.2, 'Medium': 0.5, 'High': 0.9},
            'Traffic Accident': {'Low': 0.1, 'Medium': 0.4, 'High': 0.8}
        }
        
        return risk_factors.get(hazard_type, {}).get(severity, 0.0)

    def update_edge_risk(self):
        """
        Update edge weights (cost) based on the hazard data.
        For example, if a fire hazard is found near a certain edge, 
        it increases the risk and thus the evacuation cost.
        """
        for u, v, data in self.graph.edges(data=True):
            # Check the hazards for nodes u and v
            hazard_u = self.graph.nodes[u].get('hazard')
            hazard_v = self.graph.nodes[v].get('hazard')

            # If either node has a hazard, we increase the risk for that edge
            hazard_risk = 0
            if hazard_u:
                hazard_risk += hazard_u['risk_level']
            if hazard_v:
                hazard_risk += hazard_v['risk_level']

            # Normalize the risk to a value between 0 and 1
            total_risk = min(hazard_risk, 1.0)
            data['cost'] = data.get('length', 100) * (1 + total_risk)

    def save_hazard_data(self, filename='hazard_data.json'):
        """
        Save the collected hazard data to a JSON file.
        """
        with open(filename, 'w') as file:
            json.dump(self.hazards, file, indent=4)
    
    def load_hazard_data(self, filename='hazard_data.json'):
        """
        Load hazard data from a saved JSON file.
        """
        with open(filename, 'r') as file:
            self.hazards = json.load(file)
        
        # Reattach the hazard data to the graph nodes
        for hazard in self.hazards:
            self.graph.nodes[hazard['node']]['hazard'] = hazard

    def get_hazard_summary(self):
        """
        Provide a summary of the collected hazards.
        """
        hazard_df = pd.DataFrame(self.hazards)
        return hazard_df.groupby(['type', 'severity']).agg(
            count=('node', 'count'),
            avg_risk=('risk_level', 'mean')
        ).reset_index()

# Usage Example

if __name__ == "__main__":
    # Create a sample graph (you would use your actual evacuation graph here)
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2, 3])
    G.add_edges_from([(0, 1), (1, 2), (2, 3)])

    # Initialize the Hazard Collector with the graph
    hazard_collector = HazardCollector(G)

    # Collect hazard data (this could be triggered by a scheduled task or event)
    hazard_collector.collect_hazard_data()

    # Update the edge risks based on collected hazards
    hazard_collector.update_edge_risk()

    # Save the hazard data to a file
    hazard_collector.save_hazard_data()

    # Optionally, load hazard data from a previous run
    hazard_collector.load_hazard_data()

    # Display a summary of the hazards
    hazard_summary = hazard_collector.get_hazard_summary()
    print(hazard_summary)
