from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import docker
import threading
import psutil
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

client = docker.from_env()

deployments = []

# ---------------- DASHBOARD ----------------
@app.route("/")
def index():
    return render_template("dashboard.html")


# ---------------- DEPLOY ----------------
@app.route("/deploy", methods=["POST"])
def deploy():
    project = request.form.get("project")

    try:
        # Build image
        image, logs = client.images.build(path=".", dockerfile="Dockerfile.demo", tag=project)

        # Run container (random port)
        container = client.containers.run(
            project,
            detach=True,
            ports={'80/tcp': None}
        )

        container.reload()
        port = container.attrs['NetworkSettings']['Ports']['80/tcp'][0]['HostPort']

        deployments.append({
            "project": project,
            "id": container.id,
            "port": port
        })

        # Start logs streaming
        threading.Thread(target=stream_logs, args=(container.id,)).start()

        return jsonify({
            "status": "success",
            "url": f"http://13.126.46.108:{port}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- GET DEPLOYMENTS ----------------
@app.route("/deployments")
def get_deployments():
    return jsonify(deployments)


# ---------------- LOGS ----------------
def stream_logs(container_id):
    try:
        container = client.containers.get(container_id)
        for log in container.logs(stream=True, follow=True):
            socketio.emit("logs", log.decode("utf-8"))
    except Exception as e:
        socketio.emit("logs", f"Error: {str(e)}")


# ---------------- CPU + ALERTS ----------------
@app.route("/cpu")
def cpu():
    cpu = psutil.cpu_percent(interval=1)

    socketio.emit("cpu", cpu)

    # Lower threshold for demo
    if cpu > 5:
        socketio.emit("alert", f"⚠️ High CPU Usage: {cpu}%")

    return jsonify({"cpu": cpu})


# ---------------- START/STOP ----------------
@app.route("/start/<id>")
def start(id):
    client.containers.get(id).start()
    return "started"


@app.route("/stop/<id>")
def stop(id):
    client.containers.get(id).stop()
    return "stopped"


@app.route("/delete/<id>")
def delete(id):
    client.containers.get(id).remove(force=True)
    return "deleted"


# ---------------- GITHUB WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if data.get("ref") == "refs/heads/main":
        # Auto deploy on push
        deploy_auto("auto-app")

    return "OK"


def deploy_auto(name):
    try:
        image, _ = client.images.build(path=".", dockerfile="Dockerfile.demo", tag=name)

        container = client.containers.run(
            name,
            detach=True,
            ports={'80/tcp': None}
        )

        container.reload()
        port = container.attrs['NetworkSettings']['Ports']['80/tcp'][0]['HostPort']

        deployments.append({
            "project": name,
            "id": container.id,
            "port": port
        })

        threading.Thread(target=stream_logs, args=(container.id,)).start()

    except Exception as e:
        print(e)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5003)
