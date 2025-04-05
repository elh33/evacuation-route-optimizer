# Real-Time Evacuation Route Optimization

A machine learning system for real-time evacuation route optimization during natural disasters.

## Overview

This project integrates heterogeneous data sources (road networks, weather, hazard maps, and traffic) with advanced machine learning models to recommend the safest and fastest evacuation routes during disaster situations.

## Features

- Real-time data collection from multiple sources
- Predictive weather and traffic modeling using LSTM networks
- Graph-based risk modeling with Graph Convolutional Networks
- Dynamic route optimization using weighted A* algorithm
- Interactive visualization of evacuation routes

## Installation

```bash
# Clone the repository
git clone https://github.com/elh33/evacuation-route-optimizer.git
cd evacuation-route-optimizer

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with your API keys and configuration
