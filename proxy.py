from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# Configuration
SUPERVISOR_URL = "http://supervisor"
API_PORT = 9999

def get_supervisor_token():
    """Get supervisor token from token file."""
    try:
        if os.path.exists("/data/supervisor.token"):
            with open("/data/supervisor.token", "r") as f:
                return f.read().strip()
        return None
    except:
        return None

@app.route("/api/hassio/addons", methods=["GET"])
def list_addons():
    """List all add-ons."""
    token = get_supervisor_token()
    if not token:
        return jsonify({"result": "error", "message": "No supervisor token"}), 500
    
    try:
        response = requests.get(
            f"{SUPERVISOR_URL}/addons",
            headers={"Authorization": f"Bearer {token}"}
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"result": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("Starting Home Assistant Supervisor API Proxy...")
    print(f"Listening on port {API_PORT}")
    app.run(host="0.0.0.0", port=API_PORT)