#!/usr/bin/env python3
import logging
import sys
import os
from flask import Flask, jsonify

# Set up logging like the working example
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

@app.route("/")
def hello():
    _LOGGER.info("Root endpoint called")
    return "Hello from Supervisor API Proxy!"

@app.route("/health")
def health():
    _LOGGER.info("Health endpoint called")
    return jsonify({
        "status": "healthy", 
        "message": "Supervisor API Proxy running",
        "port": 8080
    })

@app.route("/api/v1/health")
def api_health():
    _LOGGER.info("API health endpoint called")
    return jsonify({
        "status": "healthy",
        "supervisor_token_available": bool(os.environ.get('SUPERVISOR_TOKEN')),
        "supervisor_accessible": False  # Will implement later
    })

if __name__ == '__main__':
    _LOGGER.info("🚀 Starting Supervisor API Proxy")
    _LOGGER.info("Python version: %s", sys.version)
    _LOGGER.info("Working directory: %s", os.getcwd())
    
    try:
        _LOGGER.info("Starting Flask server on 0.0.0.0:8080")
        app.run(host='0.0.0.0', port=8080, debug=False)
    except Exception as e:
        _LOGGER.error("Failed to start Flask application: %s", e)
        sys.exit(1)