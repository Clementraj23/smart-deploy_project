import os
import subprocess
import time
import random
import shutil
import psutil

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO

# ---------------- APP SETUP ----------------
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

BASE_DIR = os.getcwd()
DEPLOY_DIR = os.path.join(BASE_DIR, "deployments")

if not os.path.exists(DEPLOY_DIR):
    os.makedirs(DEPLOY_DIR)

deployments = []


# ---------------- SOCKET DEBUG ----------------
@socketio.on("connect")
def handle_connect():
    print("🔥 CLIENT CONNECTED")


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("dashboard.html")


# ---------------- DEPLOY ----------------
@app.route("/deploy", methods=["POST"])
def deploy():
    data = request.get_json()
    repo = data.get("repo")

    if not repo:
        return jsonify({"error": "Repo URL missing"}), 400

    try:
        repo_name = repo.split("/")[-1].replace(".git", "")
        project_path = os.path.join(DEPLOY_DIR, repo_name)

        # remove old
        if os.path.exists(project_path):
            shutil.rmtree(project_path)

        # clone repo
        subprocess.run(["git", "clone", repo, project_path], check=True)

        # check Dockerfile
        dockerfile = os.path.join(project_path, "Dockerfile")
        if not os.path.exists(dockerfile):
            return jsonify({"error": "❌ No Dockerfile found in repo"}), 400

        image_name = f"{repo_name}_img"
        container_name = f"{repo_name}_{random.randint(1000,9999)}"

        # build image
        subprocess.run(
            ["docker", "build", "-t", image_name, project_path],
            check=True
        )

        # random port
        port = random.randint(5001, 5999)

        # run container
        subprocess.run([
            "docker", "run", "-d",
            "-p", f"{port}:5000",
            "--name", container_name,
            image_name
        ], check=True)

        url = f"http://13.126.46.108:{port}"

        deployments.append({
            "name": repo_name,
            "url": url
        })

        socketio.emit("logs", f"🚀 Deployed {repo_name} → {url}\n")

        return jsonify({"url": url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- GET DEPLOYMENTS ----------------
@app.route("/deployments")
def get_deployments():
    return jsonify(deployments)


# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        repo = data["repository"]["clone_url"]
        return deploy()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- CPU MONITOR ----------------
def cpu_monitor():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        print("CPU:", cpu)

        socketio.emit("cpu", cpu)

        if cpu > 50:
            socketio.emit("alert", f"⚠️ High CPU: {cpu}%")

        time.sleep(2)


# ---------------- LOG STREAM ----------------
def log_stream():
    while True:
        socketio.emit("logs", "📜 System running...\n")
        time.sleep(5)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("🚀 Starting SmartDeploy AI...")

    socketio.start_background_task(cpu_monitor)
    socketio.start_background_task(log_stream)

    socketio.run(app, host="0.0.0.0", port=5003)
