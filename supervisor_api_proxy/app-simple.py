#!/usr/bin/env python3
import sys
import os

print("🚀 Starting simple test app...")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

try:
    print("📦 Importing Flask...")
    from flask import Flask, jsonify
    print("✅ Flask imported successfully")
    
    print("🔧 Creating Flask app...")
    app = Flask(__name__)
    
    @app.route("/")
    def hello():
        print("📡 / endpoint called")
        return "Hello from Supervisor API Proxy!"
    
    @app.route("/health")
    def health():
        print("🏥 /health endpoint called")
        return jsonify({"status": "healthy", "message": "Simple app running"})
    
    print("✅ Flask app configured")
    print("🌐 Attempting to start on 0.0.0.0:8080...")
    print("🔍 This should show Flask development server messages...")
    
    # Enable some Flask logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    app.run(host='0.0.0.0', port=8080, debug=True)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🔚 App has finished (this shouldn't print if Flask is running)")