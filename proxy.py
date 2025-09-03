from flask import Flask, jsonify
import requests

SUPERVISOR_TOKEN = open("/data/supervisor.token").read().strip()
SUPERVISOR_URL = "http://supervisor"

app = Flask(__name__)

@app.route("/api/hassio/addons", methods=["GET"])
def list_addons():
    r = requests.get(
        f"{SUPERVISOR_URL}/addons",
        headers={"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}
    )
    return jsonify(r.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999)
