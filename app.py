import os
import subprocess
import time
import random
import shutil
import psutil

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO

# ---------------- CONFIG ----------------
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

BASE_DIR = os.getcwd()
DEPLOY_DIR = os.path.join(BASE_DIR, "deployments")

if not os.path.exists(DEPLOY_DIR):
    os.makedirs(DEPLOY_DIR)

deployments = []


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("dashboard.html")


# ---------------- DEPLOY FUNCTION ----------------
@app.route("/deploy", methods=["POST"])
def deploy():
    data = request.get_json()
    repo = data.get("repo")

    if not repo:
        return jsonify({"error": "Repo URL missing"}), 400

    try:
        repo_name = repo.split("/")[-1].replace(".git", "")
        project_path = os.path.join(DEPLOY_DIR, repo_name)

        # remove old folder
        if os.path.exists(project_path):
            shutil.rmtree(project_path)

        # clone repo
        subprocess.run(["git", "clone", repo, project_path], check=True)

        # detect dockerfile
        dockerfile_path = os.path.join(project_path, "Dockerfile")
        if not os.path.exists(dockerfile_path):
            return jsonify({"error": "❌ No Dockerfile found in repo"}), 400

        # build image
        image_name = f"{repo_name.lower()}_img"
        subprocess.run(
            ["docker", "build", "-t", image_name, project_path],
            check=True
        )

        # generate random port
        port = random.randint(5001, 5999)

        # run container
        container_name = f"{repo_name.lower()}_{port}"

        subprocess.run([
            "docker", "run", "-d",
            "-p", f"{port}:5000",
            "--name", container_name,
            image_name
        ], check=True)

        url = f"http://13.126.46.108:{port}"

        deployments.append({
            "name": repo_name,
            "url": url,
            "container": container_name
        })

        # emit log
        socketio.emit("logs", f"\n🚀 Deployed {repo_name} at {url}\n")

        return jsonify({"url": url})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500


# ---------------- GET DEPLOYMENTS ----------------
@app.route("/deployments")
def get_deployments():
    return jsonify(deployments)


# ---------------- WEBHOOK AUTO DEPLOY ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        repo = data["repository"]["clone_url"]

        # reuse deploy logic
        return deploy()

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- CPU MONITOR ----------------
def cpu_monitor():
    while True:
        cpu = psutil.cpu_percent()

        # emit cpu
        socketio.emit("cpu", cpu)

        # alert
        if cpu > 50:
            socketio.emit("alert", f"⚠️ High CPU: {cpu}%")

        time.sleep(2)


# ---------------- LOG SIMULATION ----------------
def log_stream():
    while True:
        socketio.emit("logs", f"📜 Running... CPU stable\n")
        time.sleep(5)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("🚀 Starting SmartDeploy AI...")

    socketio.start_background_task(cpu_monitor)
    socketio.start_background_task(log_stream)

    socketio.run(app, host="0.0.0.0", port=5003)
