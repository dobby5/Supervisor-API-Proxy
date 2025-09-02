#!/bin/bash

echo "=== DIRECT STARTUP (No s6-overlay, no bashio) ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "Starting simple Flask app..."

cd /app
echo "Changed to: $(pwd)"
echo "Files: $(ls -la)"

echo "Starting Python application directly..."
python3 app-simple.py

echo "Python app exited with code: $?"