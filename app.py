from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
import subprocess, os, random, shutil, psutil, time, threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

deployments = []

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("dashboard.html")


# ---------------- GET DEPLOYMENTS ----------------
@app.route("/deployments")
def get_deployments():
    return jsonify(deployments)


# ---------------- DEPLOY ----------------
@app.route("/deploy", methods=["POST"])
def deploy():
    data = request.json
    repo_url = data.get("repo")

    if not repo_url:
        return jsonify({"error": "No repo URL provided"}), 400

    name = repo_url.split("/")[-1].replace(".git", "")
    port = random.randint(5005, 5999)

    try:
        # clean old
        if os.path.exists(name):
            shutil.rmtree(name)

        subprocess.run(["git", "clone", repo_url], check=True)

        dockerfile_path = f"{name}/Dockerfile"

        # 🔥 auto dockerfile
        if not os.path.exists(dockerfile_path):
            with open(dockerfile_path, "w") as f:
                f.write("""FROM python:3.9
WORKDIR /app
COPY . .

RUN pip install -r requirements.txt || pip install flask gunicorn

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
""")

        subprocess.run(["docker", "build", "-t", name, name], check=True)

        container_name = f"{name}_{port}"

        subprocess.run(["docker", "rm", "-f", container_name],
                       stderr=subprocess.DEVNULL)

        subprocess.run([
            "docker", "run", "-d",
            "-p", f"{port}:5000",
            "--name", container_name,
            name
        ], check=True)

        url = f"http://13.126.46.108:{port}"

        deployment = {
            "project": name,
            "url": url,
            "container": container_name,
            "logs": "🚀 Running"
        }

        deployments.append(deployment)

        # 🔥 realtime push
        socketio.emit("new_deploy", deployment)

        return jsonify({"url": url})

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- CPU MONITOR ----------------
def monitor_cpu():
    while True:
        cpu = psutil.cpu_percent(interval=2)

        socketio.emit("cpu", cpu)

        if cpu > 70:
            socketio.emit("alert", f"🔥 High CPU Usage: {cpu}%")

        time.sleep(2)


# ---------------- LOG STREAM ----------------
def stream_logs():
    while True:
        for d in deployments:
            try:
                logs = subprocess.getoutput(
                    f"docker logs {d['container']} --tail 10"
                )

                socketio.emit("logs", {
                    "project": d["project"],
                    "logs": logs
                })
            except:
                pass

        time.sleep(4)


# ---------------- START THREADS ----------------
threading.Thread(target=monitor_cpu, daemon=True).start()
threading.Thread(target=stream_logs, daemon=True).start()


# ---------------- MAIN ----------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5003)
