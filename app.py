from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import subprocess
import os
import random
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

deployments = []

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("dashboard.html")

# ---------------- DEPLOY FUNCTION ----------------
@app.route("/deploy", methods=["POST"])
def deploy():
    data = request.json
    repo_url = data.get("repo")

    if not repo_url:
        return jsonify({"error": "No repo provided"}), 400

    name = repo_url.split("/")[-1].replace(".git", "")
    port = random.randint(5005, 5999)

    try:
        # Remove old project if exists
        if os.path.exists(name):
            subprocess.run(["rm", "-rf", name])

        # Clone repo
        subprocess.run(["git", "clone", repo_url], check=True)

        # Detect Dockerfile location
        docker_path = None

        if os.path.exists(f"{name}/Dockerfile"):
            docker_path = name
        elif os.path.exists(f"{name}/demo_app/Dockerfile"):
            docker_path = f"{name}/demo_app"
        else:
            return jsonify({
                "error": "❌ No Dockerfile found in repo"
            })

        # Build Docker image
        subprocess.run([
            "docker", "build", "-t", name, docker_path
        ], check=True)

        # Run container
        container_name = f"{name}_{port}"

        subprocess.run([
            "docker", "run", "-d",
            "-p", f"{port}:5000",
            "--name", container_name,
            name
        ], check=True)

        url = f"http://13.126.46.108:{port}"

        deployments.append({
            "project": name,
            "url": url,
            "logs": "✅ Deployment successful"
        })

        return jsonify({
            "message": "🚀 Deployment successful",
            "url": url
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": f"❌ Deploy failed: {str(e)}"
        })


# ---------------- GET DEPLOYMENTS ----------------
@app.route("/deployments")
def get_deployments():
    return jsonify(deployments)


# ---------------- WEBHOOK (AUTO DEPLOY) ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        repo = data["repository"]["clone_url"]
    except:
        return "Invalid payload", 400

    print("🚀 GitHub push detected:", repo)

    with app.test_request_context(json={"repo": repo}):
        return deploy()


# ---------------- CPU + ALERTS ----------------
def background_cpu():
    while True:
        value = random.randint(10, 90)
        socketio.emit("cpu", value)

        if value > 70:
            socketio.emit("alert", f"🔥 High CPU: {value}%")

        time.sleep(3)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    threading.Thread(target=background_cpu).start()
    socketio.run(app, host="0.0.0.0", port=5003)
