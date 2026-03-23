# ---------------- EVENTLET (MUST BE FIRST) ----------------
import eventlet
eventlet.monkey_patch()

# ---------------- IMPORTS ----------------
import os
import subprocess
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

        # remove old project if exists
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

        # use safe port range (matches your AWS rule)
        port = random.randint(8000, 8100)

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

        # ✅ send log to frontend
        socketio.emit("logs", f"🚀 Deployed {repo_name} → {url}\n")

        return jsonify({"url": url})

    except Exception as e:
        socketio.emit("logs", f"❌ Deployment error: {str(e)}\n")
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
        try:
            cpu = psutil.cpu_percent(interval=1)

            # ✅ emit CPU data
            socketio.emit("cpu", cpu)

            # ✅ alert
            if cpu > 50:
                socketio.emit("alert", f"⚠️ High CPU: {cpu}%")

        except Exception as e:
            print("CPU ERROR:", e)

        socketio.sleep(2)   # ✅ IMPORTANT FIX

# ---------------- LOG STREAM ----------------
def log_stream():
    while True:
        try:
            socketio.emit("logs", "📜 System running...\n")
        except Exception as e:
            print("LOG ERROR:", e)

        socketio.sleep(5)   # ✅ IMPORTANT FIX

# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("🚀 Starting SmartDeploy AI...")

    # start background workers
    socketio.start_background_task(cpu_monitor)
    socketio.start_background_task(log_stream)

    # run server
    socketio.run(app, host="0.0.0.0", port=5003)
