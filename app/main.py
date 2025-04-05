import os
import sys
# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, jsonify, request
import logging
from config import PORT, HOST, DEBUG, DEFAULT_CITY, SECRET_KEY
from app.routes import register_routes

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    
    # Configure logging
    if not DEBUG:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler("app.log"),
                logging.StreamHandler()
            ]
        )
    
    # Register all routes
    register_routes(app)
    
    @app.route('/')
    def index():
        """Home page route."""
        return render_template('index.html', default_city=DEFAULT_CITY)
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors."""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors."""
        logging.error(f"Server error: {e}")
        return render_template('500.html'), 500
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=HOST, port=PORT, debug=DEBUG)