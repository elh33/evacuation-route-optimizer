from flask import render_template, request, jsonify, redirect, url_for
from config import DEFAULT_CITY
import os
import json
import numpy as np
import logging
from pathlib import Path

# Dictionary to store loaded city data
loaded_cities = {}

def register_routes(app):
    """Register all application routes."""
    
    @app.route('/map')
    def map_view():
        """Evacuation map route."""
        city = request.args.get('city', DEFAULT_CITY)
        return render_template('evacuation_map.html', city=city)
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard route."""
        city = request.args.get('city', DEFAULT_CITY)
        return render_template('dashboard.html', city=city)
    
    @app.route('/api/load_city', methods=['POST'])
    def load_city():
        """API route to load city data."""
        data = request.json
        city = data.get('city', DEFAULT_CITY)
        
        try:
            # In a full implementation, this would load actual data from OSM
            # For now, we'll just return simulated data
            loaded_cities[city] = {
                'name': city,
                'nodes': np.random.randint(1000, 10000),
                'edges': np.random.randint(2000, 20000)
            }
            
            logging.info(f"Loaded city: {city} with {loaded_cities[city]['nodes']} nodes and {loaded_cities[city]['edges']} edges")
            
            return jsonify({
                'status': 'success',
                'city': city,
                'nodes': loaded_cities[city]['nodes'],
                'edges': loaded_cities[city]['edges']
            })
            
        except Exception as e:
            logging.error(f"Error loading city {city}: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Error loading city data: {str(e)}"
            }), 500
    
    @app.route('/api/find_routes', methods=['POST'])
    def find_routes():
        """API route to find evacuation routes."""
        try:
            data = request.json
            city = data.get('city', DEFAULT_CITY)
            start = data.get('start', '')
            end = data.get('end', '')
            
            # Simulate finding routes (in a full implementation this would use the A* algorithm)
            # For demonstration, generate some random routes
            num_routes = 3
            routes = []
            
            for i in range(num_routes):
                # Generate a random route
                routes.append({
                    'id': i,
                    'path': generate_fake_route(start, end),
                    'distance': np.random.randint(2000, 10000),  # meters
                    'time': np.random.randint(5, 30),  # minutes
                    'risk_level': round(np.random.uniform(0.1, 0.9), 2)
                })
            
            return jsonify({
                'status': 'success',
                'city': city,
                'start': start,
                'end': end,
                'routes': routes
            })
            
        except Exception as e:
            logging.error(f"Error finding routes: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Error finding evacuation routes: {str(e)}"
            }), 500
    
    @app.route('/api/weather')
    def weather_data():
        """API route for weather data."""
        try:
            city = request.args.get('city', DEFAULT_CITY)
            
            # Simulate weather data (would use a real API in production)
            weather = {
                'temperature': round(np.random.uniform(10, 30), 1),
                'humidity': round(np.random.uniform(30, 90), 1),
                'wind_speed': round(np.random.uniform(0, 20), 1),
                'precipitation': round(np.random.uniform(0, 30), 1),
                'description': np.random.choice(['Clear', 'Cloudy', 'Rain', 'Storm', 'Snow'])
            }
            
            return jsonify({
                'status': 'success',
                'city': city,
                'weather': weather
            })
            
        except Exception as e:
            logging.error(f"Error fetching weather data: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Error fetching weather data: {str(e)}"
            }), 500
    
    @app.route('/api/hazards')
    def hazards_data():
        """API route for hazard data."""
        try:
            city = request.args.get('city', DEFAULT_CITY)
            
            # Simulate hazard data
            hazard_types = ['flood', 'fire', 'storm', 'chemical', 'landslide']
            num_hazards = np.random.randint(1, 5)
            
            hazards = []
            for _ in range(num_hazards):
                hazards.append({
                    'type': np.random.choice(hazard_types),
                    'severity': round(np.random.uniform(0.3, 0.9), 2),
                    'location': f"{np.random.uniform(48.8, 48.9)}, {np.random.uniform(2.3, 2.4)}"
                })
            
            return jsonify({
                'status': 'success',
                'city': city,
                'hazards': hazards
            })
            
        except Exception as e:
            logging.error(f"Error fetching hazard data: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Error fetching hazard data: {str(e)}"
            }), 500

# Helper function to generate fake route coordinates
def generate_fake_route(start, end):
    """Generate a fake route between two points for demonstration."""
    # Parse start and end coordinates
    try:
        start_lat, start_lng = map(float, start.split(','))
        end_lat, end_lng = map(float, end.split(','))
        
        # Generate intermediate points for a realistic path
        num_points = np.random.randint(5, 15)
        
        # Linear interpolation with some random variation
        lats = np.linspace(start_lat, end_lat, num_points)
        lngs = np.linspace(start_lng, end_lng, num_points)
        
        # Add some randomness
        lats += np.random.normal(0, 0.001, num_points)
        lngs += np.random.normal(0, 0.001, num_points)
        
        # Ensure start and end points are exact
        lats[0], lngs[0] = start_lat, start_lng
        lats[-1], lngs[-1] = end_lat, end_lng
        
        # Format as coordinates
        route = [f"{lat},{lng}" for lat, lng in zip(lats, lngs)]
        return route
        
    except Exception:
        # Return a default route if parsing fails
        return [
            f"{48.85},{2.35}",
            f"{48.855},{2.355}",
            f"{48.86},{2.36}",
            f"{48.865},{2.365}"
        ]