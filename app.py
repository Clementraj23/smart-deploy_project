from flask import Flask, request, jsonify, render_template
import subprocess
import os
import random
import shutil

app = Flask(__name__)

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
        # 🔥 CLEAN OLD PROJECT
        if os.path.exists(name):
            shutil.rmtree(name)

        subprocess.run(["git", "clone", repo_url], check=True)

        project_path = name
        dockerfile_path = os.path.join(project_path, "Dockerfile")

        # 🔥 AUTO CREATE DOCKERFILE (SMART)
        if not os.path.exists(dockerfile_path):
            print("⚡ Creating Dockerfile automatically")

            with open(dockerfile_path, "w") as f:
                f.write("""FROM python:3.9
WORKDIR /app
COPY . .

RUN pip install -r requirements.txt || pip install flask gunicorn

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
""")

        # 🔥 BUILD IMAGE
        subprocess.run([
            "docker", "build", "-t", name, project_path
        ], check=True)

        container_name = f"{name}_{port}"

        # 🔥 REMOVE OLD CONTAINER IF EXISTS
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            stderr=subprocess.DEVNULL
        )

        # 🔥 RUN CONTAINER
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
            "logs": "🚀 Deployment successful"
        })

        return jsonify({
            "message": "Deployed successfully",
            "url": url
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": f"Deployment failed: {str(e)}"
        })


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
