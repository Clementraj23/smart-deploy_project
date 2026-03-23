import os
import time
import threading
import subprocess
import psutil

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

deployments = []

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("dashboard.html")

# ---------------- CPU API ----------------
@app.route("/cpu")
def cpu():
    return jsonify({"cpu": psutil.cpu_percent()})

# ---------------- BACKGROUND CPU ----------------
def background_cpu():
    while True:
        cpu_value = psutil.cpu_percent()
        socketio.emit("cpu", {"cpu": cpu_value})

        if cpu_value > 70:
            socketio.emit("alert", f"🔥 High CPU: {cpu_value}%")

        time.sleep(3)

# ---------------- DEPLOY FUNCTION ----------------
@app.route("/deploy", methods=["POST"])
def deploy():
    data = request.get_json()
    repo = data.get("repo")

    if not repo:
        return jsonify({"error": "No repo URL provided"}), 400

    name = repo.split("/")[-1].replace(".git", "")
    port = 5000 + len(deployments) + 1

    try:
        # Remove old folder if exists
        if os.path.exists(name):
            subprocess.run(["rm", "-rf", name])

        # Clone repo
        subprocess.run(["git", "clone", repo], check=True)

        # Ensure Dockerfile exists
        if not os.path.exists(f"{name}/Dockerfile"):
            return jsonify({"error": "No Dockerfile found in repo"}), 400

        # Build Docker image
        subprocess.run(["docker", "build", "-t", name, "."], cwd=name, check=True)

        # Remove old container if exists
        subprocess.run(["docker", "rm", "-f", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Run container
        subprocess.run([
            "docker", "run", "-d",
            "-p", f"{port}:5000",
            "--name", name,
            name
        ], check=True)

        url = f"http://{request.host.split(':')[0]}:{port}"

        deployments.append({
            "name": name,
            "url": url,
            "logs": "🚀 Container started successfully"
        })

        return jsonify({"url": url})

    except Exception as e:
        return jsonify({"error": str(e)})

# ---------------- GET DEPLOYMENTS ----------------
@app.route("/deployments")
def get_deployments():
    return jsonify(deployments)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    threading.Thread(target=background_cpu, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5003)
