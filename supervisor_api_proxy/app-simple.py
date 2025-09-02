#!/usr/bin/env python3

print("🚀 Starting simple test app...")

try:
    from flask import Flask, jsonify
    print("✅ Flask imported successfully")
    
    app = Flask(__name__)
    
    @app.route("/")
    def hello():
        return "Hello from Supervisor API Proxy!"
    
    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "message": "Simple app running"})
    
    print("✅ Flask app configured")
    print("🌐 Starting on 0.0.0.0:8080...")
    
    app.run(host='0.0.0.0', port=8080, debug=False)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Error starting app: {e}")
    exit(1)